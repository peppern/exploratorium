import json, urllib2, time, datetime, re, redis

maxpages = 10		# Don't Suck Too Much
sleep_delay = 1000	# Conference Bandwidth
r = redis.Redis(host='localhost', port=6379, db=0)

def count_words(string):
	string = string.lower()
	string = re.sub("[^A-Za-z\s]", '', string)
	string = re.sub("\s+", ' ', string)
	words = string.split(' ')
	return words

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
		comment_grab(subreddit, "http://reddit.com/%s" % c)

def process_comment(source, comment, parent):
	if not 'body' in comment:
		if 'title' in comment:
			comment['body'] = comment['title']
		else:
			return
	
	comment_id = comment['name']
	comment_body = comment['body']
	comment_author = comment['author']
	comment_datestamp = comment['created_utc']
	
	date_bucket = datetime.datetime.fromtimestamp(comment_datestamp).strftime("%Y-%m-%d:%H")
	for word in count_words(comment['body']):
		# print "HINCRBY %s:%s %s 1" % (source, date_bucket, word)
		# r.hincrby("%s:%s" % (source, date_bucket), word, 1)
		print "ZINCRBY %s:%s 1 %s" % (source, date_bucket, word)
		r.zincrby("%s:%s" % (source, date_bucket), word, 1)
	
	if not parent:
		return
	
	parent_id = parent['name']
	parent_author = parent['author']
	comment_link_id = comment['link_id']
	
	print "SADD %s:comments %s:%s" % (comment_link_id, parent_id, comment_id)
	r.sadd("%s:comments" % comment_link_id, "%s:%s" % (parent_id, comment_id))
	
	print "SADD %s:users %s:%s" % (comment_link_id, parent_author, comment_author)
	r.sadd("%s:users" % comment_link_id, "%s:%s" % (parent_author, comment_author))

def parse_comment(source, comment, parent):
	process_comment(source, comment, parent)
	if 'replies' in comment and len(comment['replies']) > 0:
		comments = comment['replies']['data']['children']
		parent = comment
		for comment_subtree in comments:
			comment = comment_subtree['data']
			if not 'body' in comment:
				continue
			parse_comment(source, comment, parent)
			parent = comment

def comment_grab(source, url):
	"""Accepts a url for a reddit comment thread and puts the time-stamped word counts into redis"""
	url = url+".json"
	json_comments = json.loads(urllib2.urlopen(url).read())
	parent = json_comments[0]['data']['children'][0]['data']
	parse_comment(source, parent, None)
	print "SADD %s:threads %s" % (source, parent['name'])
	r.sadd("%s:threads" % source, parent['name'])
	# oddly reduplicative
	comments = json_comments[1]['data']['children']
	for comment in comments:
		comment = comment['data']
		parse_comment(source, comment, parent)
	

subreddit_scanner('programming')
