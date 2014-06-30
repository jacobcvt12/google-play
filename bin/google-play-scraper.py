#!/usr/bin/env python

from requests import Session
from sys import argv, stderr, exit
from BeautifulSoup import BeautifulSoup
from re import sub, findall
from datetime import datetime
from time import sleep


def download_reviews(pageNo):
	"""Take page number as argument and return XHR reponse"""
	# url to pass to post
	url = 'https://play.google.com/store/getreviews'
		
	# data to pass to post
	id = appId
	pageNum = str(pageNo)
	reviewSortOrder = '4'
	reviewType = '0'
	token = 'Uotn4GEGmKSYJwq2keRT5sc05nQ:1403795571950'
	xhr = '1'
	
	# put together data dict to pass to POST
	data_dict = {
		'id'			:	id,
		'pageNum'		:	pageNum,
		'reviewSortOrder'	:	reviewSortOrder,
		'reviewType'		:	reviewType,
		'xhr'			:	xhr
	}
	
	# header info to pass to post
	userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0'
	Referer = 'https://play.google.com/store/apps/details?id=%s' % appId
	
	# put together header dict to pass to POST
	header_dict = {
		'userAgent'		:	userAgent,
		'Referer'		:	Referer
	}
	
	# print current page number to stderr
	if not (pageNo + 1) % 10:
        	stderr.write('Downloading page %d\n' % (pageNo + 1))
	
	# pass parameters to POST
	response = session.post(url=url, data=data_dict, headers=header_dict)
	clean_response = decode_response(response.text)
	
	if len(clean_response) < 100:
		# end of reviews
		return([])
    
	# check for CAPTCHA
	if 'captcha' in clean_response.lower():
		stderr.write('CAPTCHA found at review page %d\n' % (pageNo + 1))
		exit(1)

	# return(clean_response)
	reviews = parse_html(clean_response)
	
	return(reviews)
	
	
def decode_response(response):
	# encode all decoded html
	decoded_1 = response.replace('\u003c', '<').replace('\u003e', '>')
	decoded_2 = decoded_1.replace('\u003d', '=').replace('\u0026', '&')
	decoded_3 = decoded_2.replace('&amp;', '&').replace('\\"', '"')
	
	# remove extra few characters at beginning
	# and end
	
	start = decoded_3.find("<div")
	end = decoded_3.rfind("</div>") + 6
	
	html_only = decoded_3[start:end]
	
	return(html_only)

	
def parse_html(response):
	# store processed reviews here
	review_list = []
	
	# use BeautifulSoup to parse html
	soup = BeautifulSoup(response)
	
	# get the root of all div tags
	divTags = soup.findAll('div')
	
	# store and manually process first review
	firstReview = divTags[0]
	
	# process first review
	review_list.append(extract_info(firstReview))
	
	# iterate over siblings of first review
	for review in firstReview.nextSiblingGenerator():
		# sometimes the next sibling is not a review
		# when this is the case, there is no name attribute
		# check for this and skip if that's the case
		
		if hasattr(review, 'name'):
			# some 'reviews' are developer response
			# skip these by checking the class
			if review['class'] == 'single-review':
				review_list.append(extract_info(review))
		else:
			# nothing here
			pass
			
	return([x for x in review_list if x is not None])
			

def extract_info(review):
	children = review.findChildren()
	
	# when a review is left by an anonymous person,
	# there are 22 children, so the relevant children
	# are shifted down by one place
	indices = [6, 11, 19]
	
	if len(children) == 22:
		indices = [x - 1 for x in indices]
	
	try:
		review_date = sub('\n\s{1,}', '', children[indices[0]].contents[0])
	
		# convert date to standard format
		review_date = datetime.strptime(review_date, 
										'%B %d, %Y').strftime('%Y-%m-%d')
		review_rate = findall('[0-9]{2,3}', children[indices[1]]['style'])[0]
		review_stars = str(int(review_rate) / 20) # convert to stars
		review_text = children[indices[2]].contents[2]
	
		# clean text
		review_text = review_text.replace('"', "'").replace('|', '')
		review_text = review_text.replace('\n', '')
	
	except IndexError:
		# seems like these are all foreign language reviews
		stderr.write('Found unparsable review\n\n\n')
		return None

	# create a dictionary of the review to return
	review_dict = {
		'date'      :    review_date,
		'rating'    :    review_stars,
		'text'      :    review_text
	}
	
	return(review_dict)

	
if __name__ == '__main__':
	# appId = 'com.marriott.mrt'
	if not len(argv) - 1:
		stderr.write('Usage: \n\t%s android-app-id\n' % argv[0])
		exit(1)
		
	appId = argv[1]
	session = Session()
	session.head('https://play.google.com/store/apps/details?id=%s' % appId)
	
	i = 0
	all_reviews = []
	dup_counts = 0
	
	while True:		
		reviews = download_reviews(i)
		if not len(reviews):
			stderr.write('No more accessible reviews\n')
			break
			
		old_count = len(set([x['text'] + x['rating'] + x['text'] \
							 for x in all_reviews]))
		all_reviews += reviews
		new_count = len(set([x['text'] + x['rating'] + x['text'] \
							 for x in all_reviews]))
		if new_count == old_count:
			# only duplicate reviews added. exit program
			# weirdly, google lets you access more pages,
			# even when there are more pages
			# it's possible that you will get a few duplicate
			# reviews in your output, but this check will
			# catch the duplicates pretty quickly
			dup_count += 1
			stderr.write('Only duplicates found on page %d\n' % (i + 1))			
			
			if dup_count > 3:
				stderr.write('Duplicates found 3x in a row. Ending.\n')
				break
				
		else:
			dup_count = 0
				
			# print downloaded reviews
			for review in reviews:
				print review['date'] + '|' + \
					review['rating'] + '|' + \
					review['text'].encode('ascii', 'ignore')
			
		# download next page after sleeping
		# to try to avoid captcha
		i += 1
		sleep(5)
		
	exit(0)
