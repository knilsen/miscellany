#! /Users/karlnilsen/bin/anaconda/bin/python

import os
import re
from collections import Counter
import csv
from bs4 import BeautifulSoup

def extract_text(files):

	cleans = {'=\\n': '', '<=\\n/span>': '', '=\\nspan>': ''}
	subs = sorted(cleans, key = len, reverse = True)
	rexp = re.compile('|'.join(map(re.escape, subs)))

	spans = []
	for email in files:
		with open(email, 'rb') as f:
			raw_text = str(f.read())
			raw_text = rexp.sub(lambda match: cleans[match.group(0)], raw_text)
			email = BeautifulSoup(raw_text, 'lxml')
		for span in email.find_all('span'):
			spans.append(span.text)

	spans = [i.strip() for i in spans]
	companies = [i for i in spans if not (i == ''
										or '-' in i
										or 'reviews' in i
										or 'opportunities for you' in i
										or ', VA' in i
										or ', DC' in i
										or ', MD' in i)]
	# states = [i for i in spans if (', VA' in i
	#									or ', DC' in i
	#									or ', MD' in i)]

	companies = [i.strip() for i in companies]
	companies = Counter(companies)
	with open('/Users/karlnilsen/Downloads/company_data.csv', 'w') as f:
		writer = csv.writer(f)
		for key, value in companies.items():
			writer.writerow([key, value])

def main():

	base_path = '/Users/karlnilsen/apps/data/email/companies/'
	files = []
	for root, dirnames, filenames in os.walk(base_path):
		for filename in filenames:
			if filename.endswith('.emlx'):
				files.append(os.path.join(root, filename))
	extract_text(files)


if __name__ == '__main__':
    main()
