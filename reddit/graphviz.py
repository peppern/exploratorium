import redis, re

r = redis.Redis(host='localhost', port=6379, db=0)

def dotify_line(line):
	return "%s\n" % re.sub(":", " -> ", line)

def dotify_thread(thread_id):
	users = r.smembers("%s:users" % thread_id)
	
	user_f = open("%s.users.dot" % thread_id, 'w')
	user_f.write("digraph {\n")
	for edge in users:
		user_f.write(dotify_line(edge))
	user_f.write("}")
	
	comments = r.smembers("%s:comments" % thread_id)
	
	comment_f = open("%s.comments.dot" % thread_id, 'w')
	comment_f.write("digraph {\n")
	for edge in comments:
		comment_f.write(dotify_line(edge))
	comment_f.write("}")

# after running reddit_grab.py,
# redis> keys *
#  1) "gaming:2011-06-22:00"
#  2) "t3_i5ytc:users"
#  3) "gaming:2011-06-21:20"
#  4) "gaming:2011-06-22:01"
#  5) "gaming:2011-06-22:02"
#  6) "gaming:2011-06-21:21"
#  7) "gaming:2011-06-21:22"
#  8) "gaming:2011-06-21:23"
#  9) "t3_i5vwg:users"
# 10) "t3_i5ytc:comments"
# 11) "t3_i5rto:users"
# 12) "gaming:2011-06-21:18"
# 13) "t3_i5vwg:comments"
# 14) "gaming:2011-06-21:19"
# 15) "gaming:threads"
# 16) "t3_i5rto:comments"
# redis> smembers gaming:threads
# 1) "t3_i5vwg"
# 2) "t3_i5ytc"
# 3) "t3_i5rto"
dotify_thread("t3_i1lgy")