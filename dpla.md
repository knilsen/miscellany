# Getting started with the Digital Public Library of America (DPLA) API

*This post was my contribution to a longer post on the [Digital Systems and Stewardship](http://www.lib.umd.edu/dss) blog of the University of Maryland Libraries. [Read the full post](http://dssumd.wordpress.com/2014/04/24/a-brief-introduction-to-apis/).*
            	
[DPLA](http://dp.la/) has a web service API that provides programmatic access to over 7 million metadata records collected from a variety of libraries, archives, and museums. While the query process can seem complicated at first, the basic actions are pretty simple: you submit queries in HTTP and receive responses in JSON-LD. The responses won't be especially readable, but it's important to keep in mind that JSON (and HTTP) will typically be consumed by programs rather than humans. If you build an application for non-technical users, you probably won't show them the HTTP queries or the JSON responses at all—instead, you'll create an interface that makes query design and response visualization more user-friendly. That being said, you have to understand the query design and response structure if you want to produce applications that satisfy your users' expectations and support their research methods. To help you understand the possibilities and limitations of their API, DPLA provides a [detailed guide](http://dp.la/info/developers/codex/) to query design and response structure.

Before you can use the API, you need to [get a personal API key from DPLA](http://dp.la/info/developers/codex/policies/). Your key acts as a unique username, and you have to include your key in every HTTP query. DPLA uses the API key as mechanism for protecting their system against abusive or excessive users. For example, if your queries burden their system, they can block your API key. As a rule, you shouldn't share your API key with anyone.
            	
At Emerging Technologies Discussion Group (UMD Libraries, 2014-04-22), I demonstrated a few queries written in Python, but you can write the same queries in other programming languages. The code is merely a set of instructions for sending the HTTP query, receiving the JSON response, and manipulating the results.
            	
Here's a simple script that submits a query for `bicycle` in any metadata field, returns only 10 results, and prints the result:
				
```python
# load additional functionality into your session
import urllib, json

# build your query and submit to the API
api_call = urllib.urlopen('http://api.dp.la/v2/items?q=bicycle&amp;page_size=10&amp;api_key=YOUR_API_KEY_GOES_HERE')

results = json.load(api_call)

# print the response
print(results)
```
				
To improve the readability somewhat, you could print the results with this command:</p>
				
```python
print(json.dumps(results, indent=4))
```				

If we run this code, we receive 10 results (as expected). Before we consider a more complex example, it's important to understand which 10 records, of all the relevant items in DPLA, we received. There are close to 2500 items in DPLA that contain "bicycle" in the metadata, so why did we receive these particular records? Are they the earliest 10 records in the database by data of publication, the most recent, a random sample, the latest 10 additions to the database, or another set? We should probably contact DPLA to find out exactly how their system works. Given that we don't know the answer just yet, we wouldn't want to draw any conclusions from the results. (Even if we requested all 2500 items, we should still ask questions about the provenance, scope, and representativeness of the results.) DPLA provides various parameters for limiting and sorting data, such as temporal and spatial parameters, and these techniques can help us make our results interpretable.
				
Here's a script that builds a more complex query. It submits a query for "bicycle" in any metadata field, restricts the results to photographs, returns only the text description that accompanies each item, returns up to 400 results, and saves the text descriptions to a plain text file. The script removes any items that return 0 (no description found in the metadata), so the actual number of results may be less than 400. (Code updated 2014-05-21.)
				
```python
import urllib, json

txt_file = open("descriptions.txt", "w")

api_call = urllib.urlopen('http://api.dp.la/v2/items?q=bicycle&sourceResource.format=Photographs&fields=sourceResource.description&page_size=400&api_key=YOUR_API_KEY_GOES_HERE')

results = json.load(api_call)

for item in results.get('docs', 0):
    text = item.get('sourceResource.description', 0)
    if text != 0:
        text = text.encode('utf-8')
        txt_file.write(text + '\n')

text_file.close()
```
				
In this example, we constrained the responses to a particular metadata element (text descriptions), illustrating that we can easily retrieve only the information that interests us and skip the rest. Moreover, we can also retrieve hundreds or thousands of results in seconds. Imagine how long it would take to copy text descriptions by hand from DPLA's user interface! Here are three examples from the descriptions:
				
> Three men, one in uniform (police?), adjusting the wheel of a bicycle on a dirt track, with onlookers on the bleachers in background. Probably a gathering of students at the University of North Carolina-Chapel Hill.
				
> The reverend Mirko Mikolasek rides a bicycle which had been made by the Evangelical Church of Cameroon. He is surrounded by children.; Mirko Mikolasek is a missionary of the Société des missions évangéliques de Paris (Paris evangelical mission society).

> 3 images. Bicycle trip, 3 September 1958. Gary Swanson--22 years (California Institute of Technology fellowship winner, returns from 4500-mile bicycle trip). ; Caption slip reads: "Photographer: Mack. Date: 1958-09-03. Reporter: Farrell. Assignment: Cyclist. Special instructions: Early Friday. 29-30-4: Gary Swanson, 22, Caltech Fellowship winner returns from 4500-mile bicycle trip.
	
   
Having retrieved the descriptions and saved them in a text file, we could proceed to analyze them in various ways. The descriptions may tell us something about the social and cultural history of bicycles and bicycling in America and elsewhere. Content analysis or natural language processing could be productive approaches.        

2014-05-17
