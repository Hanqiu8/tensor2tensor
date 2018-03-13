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
from whoosh import index
from whoosh.fields import *
from whoosh.qparser import *
from whoosh.collectors import TimeLimitCollector, TimeLimit

from pyspark import SparkContext, SparkConf

INPUTS_FILE = "inputs.txt"
TARGETS_FILE = "targets.txt"

class QueryIndex:
	""" Creates a QueryIndex object and the associated index file
	to go with it, or if an index file of the desired name already
	exists, creates a QueryIndex object that accesses that file.
	
	Args:
		name - name of the desired index
		recordFiles - filename pattern for files containing tfrecords 
			with input and target values to be indexed.
		vocabFile - filename of a file containing the vocabulary for
			the tfrecord inputs and targets
	"""

	"""Data locations, replace with directory to respective language list
	Hardcoded for demo purposes
	
	Data format expected: translation pair per line in each document 
	"""



	def __init__(self,name, recordFiles, vocabFile):
		def operate(recordFiles, vocabFile):
			print "entered operate"
			if not os.path.exists("indexes"):
				print "creating index dir"
				os.mkdir("indexes")
			self.schema = Schema(query=TEXT(stored=True), target=TEXT(stored=True))
			if index.exists_in("indexes", indexname=name):
				self.ix = index.open_dir("indexes", name)
				
			else:
				if recordFiles == "" or vocabFile == "":
					print 'Cannot create index without data files. Please provide the file paths in configuration.json'
				else:
					self.ix = index.create_in("indexes", self.schema, indexname=name)
					records = self.getTfRecordsFromFiles(recordFiles)
					self.createStringFilesFromTfRecords(records, vocabFile)
					self.buildIndex(INPUTS_FILE,TARGETS_FILE)

		spark_app_name = "spark_app"
		self.conf = SparkConf().setAppName(spark_app_name).setMaster("local")
		self.sc = SparkContext(conf=self.conf)

		data = ["madam", "building"]
		distData = self.sc.parallelize(data)
		distData.map(operate(recordFiles, vocabFile))


		operate(recordFiles, vocabFile)
		self.sc.stop()

		# distData = self.sc.parallelize(data)

		# s = distData.reduce(lambda a, b: a + b)
		# print s

		# if not os.path.exists("indexes"):
		# 	print "creating index dir"
		# 	os.mkdir("indexes")
		# self.schema = Schema(query=TEXT(stored=True), target=TEXT(stored=True))
		# if index.exists_in("indexes", indexname=name):
		# 	self.ix = index.open_dir("indexes", name)
			
		# else:
		# 	if recordFiles == "" or vocabFile == "":
		# 		print 'Cannot create index without data files. Please provide the file paths in configuration.json'
		# 	else:
		# 		self.ix = index.create_in("indexes", self.schema, indexname=name)
		# 		records = self.getTfRecordsFromFiles(recordFiles)
		# 		self.createStringFilesFromTfRecords(records, vocabFile)
		# 		self.buildIndex(INPUTS_FILE,TARGETS_FILE)

	
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

	""" Returns a list of TFRecords given the data files.
	Args:
		files - path to data files (support wildcard pattern).
				e.g. If you want all files in directory "./dir", then do "./dir/*"
	"""
	def getTfRecordsFromFiles(self, files):
		import tensorflow as tf
		import glob

		filenames = glob.glob(files);
		records = []

		for filename in filenames:
			print "reading file '%s'..." % filename
			reader = tf.python_io.tf_record_iterator(filename)
			for raw_record in reader:
				record = tf.train.Example()
				record.ParseFromString(raw_record)
				
				records.append(record)
				if len(records) % 10000 == 0:
					print "read: %d" % len(records)
					break # TODO remove this line to load all records
			break # TODO remove this line to load all files
		return records


	def createStringFilesFromTfRecords(self, records, vocab):
		f=open(vocab)
		# TODO check if vocab file is always small enough to read into memory
		lines = f.readlines()
		input = ""
		target = ""
		inputs_file = open(INPUTS_FILE,"w+")
		targets_file = open(TARGETS_FILE,"w+")
		for record in records:
			for i in record.features.feature["inputs"].int64_list.value:
				if (i != 1): # remove <EOS> statements
					# remove newlines, extraneous '' marks, and change _ to space.
					input += lines[i].rstrip().replace("_", " ")[1:(len(lines[i])-2)]
			for i in record.features.feature["targets"].int64_list.value:
				if (i != 1): # remove <EOS> statements
					# remove newlines, extraneous '' marks, and change _ to space.
					target += lines[i].rstrip().replace("_", " ")[1:(len(lines[i])-2)]
			inputs_file.write(input + "\n")
			targets_file.write(target + "\n")
			input = ""
			target = ""
		inputs_file.close()
		targets_file.close()
		f.close()