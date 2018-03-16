# coding=utf-8
# Copyright 2017 The Tensor2Tensor Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" QueryIndex serves as a wrapper class for the Whoosh library.
Creating an object of this class will create an indexing file,
which can be used to efficiently store query-target pairs
obtained from a translation model.
"""



import os, os.path
import redis
from whoosh import index
from whoosh.fields import *
from whoosh.qparser import *
from whoosh.collectors import TimeLimitCollector, TimeLimit
from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections
from nearpy.storage import RedisStorage

class GraphStateQueryIndex:

	def __init__(self):
		redis_object = redis.Redis(host='localhost', port=6379, db=0)
		redis_storage = RedisStorage(redis_object)

		# Get hash config from redis
		config = redis_storage.load_hash_configuration('MyHash')

		if config is None:
		# Config is not existing, create hash from scratch, with 5 projections
			self.lshash = RandomBinaryProjections('MyHash', 5)
		else:
		# Config is existing, create hash with None parameters
			self.lshash = RandomBinaryProjections(None, None)
		# Apply configuration loaded from redis
			self.lshash.apply_config(config)
		# print("HERE")

		# Create engine for feature space of 100 dimensions and use our hash.
		# This will set the dimension of the lshash only the first time, not when
		# using the configuration loaded from redis. Use redis storage to store
		# buckets.
		self.engine = Engine(4, lshashes=[self.lshash], storage=redis_storage)
		redis_storage.store_hash_configuration(self.lshash)

	def findMatch(self, v):
		matches = self.engine.neighbours(v)
		return matches

	def addVector(self, v, trainingText):
		self.engine.store_vector(v, trainingText)

	def clearIndex(self):
		self.engine.clean_all_buckets()

	def clearHashInstance(self, name):
		self.engine.clean_buckets(name)

class QueryIndex:
	""" Creates a QueryIndex object and the associated index file
	to go with it, or if an index file of the desired name already
	exists, creates a QueryIndex object that accesses that file.
	
	Args:
		name - name of the desired index
		sourceLangDataFile - filename of a file containing data in the
			source language.
		targetLangDataFile - filename of a file containing data in the
			target language.
	"""

	"""Data locations, replace with directory to respective language list
	Hardcoded for demo purposes
	
	Data format expected: translation pair per line in each document 
	"""

	def __init__(self,name, sourceLangDataFile, targLangDataFile):
		if not os.path.exists("indexes"):
			os.mkdir("indexes")
		self.schema = Schema(query=TEXT(stored=True), target=TEXT(stored=True))
		if index.exists_in("indexes", indexname=name):
			self.ix = index.open_dir("indexes", name)
			
		else:
			if sourceLangDataFile == "" or targLangDataFile == "":
				print 'Cannot create index without data files. Please provide the file paths in configuration.json'
			else:
				self.ix = index.create_in("indexes", self.schema, indexname=name)
				self.buildIndex(sourceLangDataFile,targLangDataFile)

	
	""" 
	On init, if an index doesn't exist, build one
	"""
	
	""" USE THIS METHOD INSTEAD WHEN YOU WANT THE ENTIRE DATA FILE
		def buildIndex(self, queryLang, targLang):
		qFile = open(queryLang, 'r')
		tFile = open(targLang, 'r')
		writer = self.ix.writer()
		
		allLinesIndexed = False
		while allLinesIndexed == False:
			q = unicode(qFile.readline().strip(), "utf-8") #input sanitization
			t = unicode(tFile.readline().strip(), "utf-8")
			
			if q == '' or t == '':
				allLinesIndexed = False
			else:
				writer.add_document(query = q, target = t)

		writer.commit()
	"""

	def buildIndex(self, queryLang, targLang):
		qFile = open(queryLang, 'r')
		tFile = open(targLang, 'r')
		writer = self.ix.writer()
		
		for i in range(10000): #small value for now just to test
			q = unicode(qFile.readline().strip(), "utf-8") #input sanitization
			t = unicode(tFile.readline().strip(), "utf-8")
			writer.add_document(query = q, target = t)

		writer.commit()



	""" Adds the query-target pair passed to this method to the
	indexing file this object represents.
	
	If there is already a pair with the passed query in the index,
	that pair is replaced with the one passed to this method.
	NOTE: This is currently not working as intended.
	
	Note that these query-target pairs will always be stored as
	Unicode.
	
	Args:
	   qry, trgt - the pair in question
	"""
	def addPair(self, qry, trgt):
		self.ix.writer().add_document(query=unicode(qry),
									 target=unicode(trgt))
		self.ix.writer().commit()
	
	""" Returns a list of query-target pairs that match the search
	query passed to this method. This search is constrained to take
	at most 30 seconds.
	
	Args:
	   sq - the search query
	"""
	def searchIndex(self, sq):
		indexParser = MultifieldParser(["query", "target"], schema=self.schema).parse(unicode(sq))
		with self.ix.searcher() as s:
			collector = s.collector(limit=None)
			timed_collector = TimeLimitCollector(collector, timelimit=30.0)
			
			try:
				results = s.search_with_collector(indexParser, timed_collector)
			except TimeLimit:
				print 'Search ime limit of 30 seconds exceeded.'
			
			hits = timed_collector.results()
			
			# Convert result structure into a jsonable list
			# TODO: improve this structure
			matches = []
			for i in hits:
				matches.append({"sourcelang": i["query"],
								"targetlang": i["target"],
								"distance": (1.0/i.score)})
			return matches
