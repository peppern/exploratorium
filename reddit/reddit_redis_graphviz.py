import redis,math
from collections import defaultdict
r = redis.Redis(host='localhost', port=6379)

class smartCrawl:
	def __init__(self):
		self.done = set()
		self.word_order = []
		self.todo = []
		self.network = []
	def get_links(self,word):
		wdict = r.hgetall(word)
		trimmed = [(x,y) for (x,y) in wdict.items() if int(y)>self.thresh]
		self.todo += [x for (x,y) in trimmed if x not in self.done]
		self.network += [(word,x,y) for (x,y) in trimmed]
		self.done.add(word)
		self.word_order.append(word)
		for (x,y) in trimmed:
			self.citecounts[x]+=int(y)
	def __call__(self,seedword,thresh):
		self.citecounts = defaultdict(int)
		self.word = seedword
		self.thresh = thresh
		#print "starting with ",seedword
		self.get_links(seedword)
		counter = 1
		for word in self.todo:
			if word in self.done:
				continue
			counter += 1
			self.get_links(word)
			#print counter,"finished ",word
			#if counter % 100 == 0:
			#	self.dump(counter)
		self.filter()
		self.dump(counter)
	def filter(self):
		d = {}
		def swap(a):
			x,y = a.split("_")
			return "_".join((y,x))
		def same(a):
			x,y = a.split("_")
			if x == y:
				return True
			else:
				return False
		def sep(a):
			return a.split("_")
		for link in self.network:
			d['_'.join((link[0],link[1]))] = link[2]
		self.network = []
		for key in d.keys():
			if d.has_key(swap(key)):
				if d[swap(key)] > d[key]:
					self.network.append((sep(swap(key))[0],sep(swap(key))[1],d[swap(key)]))
				elif d[key] > d[swap(key)]:
					self.network.append((sep(key)[0],sep(key)[1],d[key]))
				elif d[key] == d[swap(key)]:
					if not same(key):
						self.network.append((sep(swap(key))[0],sep(swap(key))[1],d[swap(key)]))
						self.network.append((sep(key)[0],sep(key)[1],d[key]))
			else:
				self.network.append((sep(key)[0],sep(key)[1],d[key]))
	def dump(self,n):
		f = open('new_network.%s.%d.thresh%d.dot' % (self.word,n,self.thresh),'w')
		f.write("""digraph{
		edge [arrowsize="0.50", color="#000000"];
		""")
		print self.thresh,len(self.word_order)
		mx = max([y for (x,y) in self.citecounts.items()])
		for word in self.word_order:
			y = self.citecounts[word]
			#print (word,y)
			f.write("node [fontsize=%d]; \"%s\";\n" % (14+round((float(y)/mx)*72),word))
		for link in self.network:
			f.write("\"%s\" -> \"%s\" [weight=%s]\n" % (link[0],link[1],link[2]))
		f.write("}")
		f.close()