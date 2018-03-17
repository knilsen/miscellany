# Using Bash tools to examine databse tables

## I. Finding strings in multiple database tables

I'm working on a MySQL database that stores references to files and other external resources as `varchar` values. I want identify which tables contain such references. There are 112 tables in the database, so I don't want to query each table separately or join all the tables. I decided to try using Bash tools to search the tables.

#### 1: Dump the database

I turn the database into a text file with `mysqldump`.

```bash
mysqldump -u username -p db_name > db.sql
```

#### 2: Grep for references to a directory

In this example, I want to locate any references to a directory called `LV`. The `grep` utility will search a text file line-by-line, but MySQL dump files can contain a lot of data on each line (e.g. all the data values for a table on a single line), so for the sake of intelligibility I need to limit the search results. To reduce the output, I tell `grep` to return 30 characters of context around each match.

```bash
grep -noE '.{0,30}LV/.{0,30}' db.sql
```

Here's an example from the output:

```
1290:L,NULL,NULL,NULL),(3994669,1,'LV/HIPASSJ1247-77/9003407info.htm
1290:L,NULL,NULL,NULL),(4078671,1,'LV/6DF0956/4078671info.html',NULL
1290:L,NULL,NULL,NULL),(4087020,1,'LV/AGC182595/4087020info.html',NU
1290:L,NULL,NULL,NULL),(4614882,1,'LV/HIPASSJ1348-37/4614882info.htm
1290:L,NULL,NULL,NULL),(4689187,1,'LV/CenN/4689187info.html',NULL,'3
1290:L,NULL,NULL,NULL),(4689195,1,'LV/IKN/4689195info.html','ANGST/1
1290:L,NULL,NULL,NULL),(4689216,1,'LV/HS117/4689216info.html','ANGST
1290:,'27.91','28.08'),(5056931,1,'LV/d0934+70/5056931info.html',NUL
```

(If you try to replicate this search, your output may have a slightly different structure due to a different version of `grep`. This example uses GNU `grep` on Linux.)

The number at the beginning of each line is the line number in the `db.sql` file (added by the `-n` option to `grep`). Note that many of the matching values are on the same line in `db.sql`. Each line in the `grep` output is probably a discrete row in the same table. Next, I have to figure out what table is associated with line `1290`.

#### 2: Find the table

Judging from the tuples, line `1920` is probably an SQL `INSERT` statement. I can test that idea by examining the beginning of the line.

```bash
sed -n '1290'p db.sql | cut -c-200
```

Output:

```
INSERT INTO `` `kcmd` `` VALUES (143,1,'LV/DDO221/143info.html',NULL,'0.98',6813,'WFPC2',NULL,NULL,NULL,NULL,'20.99','20.90','21.02',NULL,NULL,NULL,'1.49','1.40','1.52','20.95','20.86','20.98','1.51','1.42'
```

So the table `kcmd` contains a references to the `LV` directory in a file system. Good to know. But how many other tables contain references to `LV`?

#### 3: Find any other tables that contain a match

To find any additional tables that contain `LV/`, I have to find all matching lines in `db.sql`. Since the same line can appear multiple times in the search results, I want to reduce the output to display only unique lines.

```bash
grep -noE 'LV/' db.sql | cut -f1 -d: | uniq -c | sort -nr
```

Output:

```bash
    340 1290
```

It looks like only line `1290` (i.e. table `kcmd`) in `db.sql` contain references to the `LV/` directory. It appears to contain 340 references. If other tables had contained `LV/`, they would have appeared in the output as line numbers and match counts. I would have then repeated my examination of the lines to identify the table names.

To see what happens when the results contain more than one table, I'll try the same approach with a file extension rather than a directory. For example, I want to find any lines that contain references to `.gif` files.

```bash
grep -noE '.gif' db.sql | cut -f1 -d: | uniq -c | sort -nr
```

```bash
   1000 2353
    343 5357
     20 2005
      1 5343
      1 1369
```

Five lines contain references to `.gif` files. Looking closer, three of these lines are SQL `INSERT` statements and each populates a table in the database. I can examine each line using a combination of techniques described above:

```bash
sed -n '2005'p db.sql | grep -oE '.{0,100}gif.{0,100}'
```

In the results, I can find references to `.gif` files such as:

line | example file
---- | ------------
2353 | 143.gif
5357 | pgc0000654.gif
2005 | http://www.cv.nrao.edu/~rfisher/Arecibo/Profiles/19465+1651.927762089.gif

Now it's a relatively simple matter to figure out the table names associated with those lines.

## II. Detecting changes in database versions

#### 1. Check for new tables

I received a new version of the database (as an `.sql` file) and I want to figure out if there are any new tables in the database. Here's a technique using `diff` to compare the old and new `.sql` files:

```bash
diff -bB --suppress-common-lines dbv1.sql dbv2.sql | grep -n 'CREATE'

8:> CREATE TABLE `k13442` (
37:> CREATE TABLE `k6dfgs` (
81:> CREATE TABLE `kcand` (
237:> CREATE TABLE `ks4gmulti` (
329:> CREATE TABLE `kwisecand` (
366:> CREATE TABLE `kwisepfw` (
```

#### 2. Check for changes to tables

Next, I want to find out if any tables have changed the number of rows and/or colummns. A handy way to get the data is to run the `mysqlshow` utility:

```bash
mysqlshow -u username -p --count dbname > tablesv2.txt
```

```bash
diff -bB tablesv1.txt tablesv2.txt

5a6
> | k13442     |        6 |         44 |
10a12
> | k6dfgs     |       20 |       8885 |
25c27,28
< | kcf2       |       49 |       8163 |
---
> | kcand      |       29 |       9060 |
> | kcf2       |       49 |       8203 |
28c31
< | kcmd       |       55 |        340 |
---
> | kcmd       |       55 |        384 |
30c33
< | kcolumns   |        7 |       2853 |
---
> | kcolumns   |        7 |       3046 |
55,56c58,59
< | kleda      |       77 |     100631 |
< | kleda_orig |       76 |     100631 |
---
> | kleda      |       77 |     100654 |
> | kleda_orig |       76 |     100654 |
69,70c72,73
< | knestnorth |       36 |      21995 |
< | knestsouth |       36 |      21043 |
---
> | knestnorth |       40 |      21995 |
> | knestsouth |       40 |      21043 |
80,81c83,84
< | kpnlf      |        8 |         52 |
< | kprofiles  |       42 |      17738 |
---
> | kpnlf      |       15 |         52 |
> | kprofiles  |       42 |      17763 |
90a94
> | ks4gmulti  |       61 |       2352 |
97c101
< | kspitphot  |       25 |       1865 |
---
> | kspitphot  |       25 |       1864 |
100c104
< | ktables    |        8 |        108 |
---
> | ktables    |        8 |        114 |
114c118,120
< | kwisephot  |       14 |        667 |
---
> | kwisecand  |       15 |       7028 |
> | kwisepfw   |       11 |        570 |
> | kwisephot  |       50 |        667 |
116c122
< | pgc        |        1 |     109253 |
---
> | pgc        |        1 |     111326 |
118,119c124
< 112 rows in set.
<
```