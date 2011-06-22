import json, urllib2, time, datetime, redis

maxpages = 10		# Don't Suck Too Much
sleep_delay = 1000	# Conference Bandwidth

def reddit_page_handler(url):
	"""Given a page of reddit stories, grabs the comment urls"""
	payload = urllib2.urlopen(url).read()
	payload = json.loads(payload)
	comment_pages = []
	for story in payload['data']['children']:
		story = story['data']
		comment_url = story['permalink']
		comment_pages.append(comment_url)
	return (comment_pages,payload['data']['after'])

def subreddit_scanner(subreddit):
	"""Given the name of a subreddit, crawl back in time grabbing comment data"""
	print "loading first page of ",subreddit
	first_page = "http://www.reddit.com/r/%s/.json" % (subreddit,)
	comment_pages,afterkey = reddit_page_handler(first_page)
	for x in xrange(maxpages):
		print "loading page ",x," of ",subreddit
		next_page="http://www.reddit.com/r/%s/.json?after=%s" % (subreddit,afterkey)
		result = reddit_page_handler(next_page)
		comment_pages += result[0]
		afterkey = result[1]
	for c in comment_pages:
		print c
		comment_grab(c)
		
def comment_grab(url):
	"""Accepts a url for a reddit comment thread and puts the time-stamped word counts into redis"""
	url = url+".json"
	json_comments = json.loads(urllib2.urlopen(url).read())
	todo = json_comments[1]['data']['children']
	for comment_subtree in todo:
		submit = {}
		submit
	
subreddit_scanner('gaming')