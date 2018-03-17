#! /Users/karlnilsen/bin/anaconda/bin/python
import argparse
import urllib.request
import sys


def download(input):

    template = "http://www.ietf.org/rfc/rfc{}.txt"
    url = template.format(input)

    try:
        raw_text = urllib.request.urlopen(url).read()

    except urllib.error.HTTPError as e:
        print("status:", e.code)
        print("reason:", e.reason)
        print("url:", e.url)
        sys.exit(1)

    rfc = raw_text.decode()

    print(rfc)


def main():

    parser = argparse.ArgumentParser(
        description="Download RFC texts and print to standard output")
    parser.add_argument("number", type=str, help="Enter an RFC number")

    args = parser.parse_args()
    rfc_num = args.number

    download(rfc_num)

if __name__ == '__main__':
    main()
