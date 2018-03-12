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

""" This program serves to test indexing.py, more specifically the
QueryIndex class implemented within it. If the class has been
implemented, this should return without errors.

NOTICE: You must have a copy of europarl-v7.de-en.de and europarl-v7.de-en.en
in the directory from which you run this script for it to function.
You can get these files with the shell command wget www.statmt.org/europarl/v7/de-en.tgz
"""

from tensor2tensor.insights import indexing as ix
import tensorflow as tf
import time
import os.path
import shutil
import sys

""" This field determines the time threshold. QueryIndex objects that take more time to init
than this field in seconds are assumed to be generated from scratch, and other indexes are assumed
to be read from an existing index on disk.
Please adjust this field to a number that seems appropriate for your computer. """

init_time_threshold = 1.0

# Check that certain necessary data files are available before testing

required_data = ["./translate_ende_wmt32k-train-00001-of-00100",
                 "./translate_ende_wmt32k-train-00002-of-00100",
                 "./vocab.ende.32768"]

for d in required_data:
	if not os.path.exists(d):
		print("You don't have certain data files needed to perform testing. Check the README to see how to get this data.")
		sys.exit()

# Setup - clean up indexes from any previous testing
if os.path.exists("./indexes"):
	shutil.rmtree("./indexes")

""" First, create the indexes to be used for search tests, and search on them """

""" English to German index - Fairly large index, a few characters are unique to German.
Data for translate_ende_wmt32k as created by t2t-datagen is best suited for these tests. """

ende_index = ix.QueryIndex("ende", "./translate_ende_wmt32k-train-00001-of-00100", "./vocab.ende.32768")
ende_results = []
ende_queries = ["session", #Purely English word
                "ich", #Purely German word
                "die", #Appears in both English and German
                "must have my", #Multiple English words
                "herr haben mein", #Multiple German words
                "in sie let", #Mix of English and German words
                "sghioghi", #Not a word anywhere
                "dem dgsgfgf last", #gibberish word, with acual words
                ""] #Empty string 

for i in range(len(ende_queries)):
	ende_results.append(ende_index.searchIndex(ende_queries[i]))

""" Search test 1: searchIndex only returns entries that satisfy query in some way """

for i in range(len(ende_results)):
	for j in range(len(ende_results[i])):
		keywords = ende_queries[i].lower().split(" ")
		kw_match_found = False
		
		for kw in keywords:
			if kw in ende_results[i][j]["targetlang"].lower() or kw in ende_results[i][j]["sourcelang"].lower():
				kw_match_found = True
			
		assert kw_match_found, "Search test 1 query %d entry %d for index ende failed" % (i, j)

print "Search test 1 passed."
									
""" Search test 2: searchIndex returns ALL entries that satisfy the query """

# target lengths, obtained from alternative parsing
ende_exp_lengths = [10, 1038, 4980, 12, 1, 22, 0, 0, 0] 
ende_actual_lengths = [len(entry) for entry in ende_results]

for i in range(len(ende_exp_lengths)):
	assert (i < len(ende_actual_lengths) and
	        ende_exp_lengths[i] == ende_actual_lengths[i]), "Search test 2 query %d for index ende failed (expected %d but got %d)" % (i, ende_exp_lengths[i], ende_actual_lengths[i])

print "Search test 2 passed."
		
""" Search test 3: searchIndex entries are returned in order of ascending distance from query"""

for i in range(len(ende_results)):
	for j in range(len(ende_results[i])):
		assert (j == 0 or
				ende_results[i][j]["distance"] >= ende_results[i][j-1]["distance"]), "Search test 3 query %d for index ende failed for entry %d" % (i, j)

print "Search test 3 passed."

print "All search tests passed."

""" Intialization test 1: When index is loaded with same name as existing index,
load time should be short, and resulting index should give same search results as previous one """

start_time = time.clock()
ende2_index = ix.QueryIndex("ende", "./translate_ende_wmt32k-train-00001-of-00100", "./vocab.ende.32768")
end_time = time.clock()

assert (end_time - start_time < init_time_threshold), "Initialization test 1 failed - took too long to load an existing index (beyond %d seconds). If this seems too unreasonable for your development environment, please edit the init_time_threshold field in index_tester.py" % (init_time_threshold)

ende2_results = []
for i in range(len(ende_queries)):
	ende2_results.append(ende2_index.searchIndex(ende_queries[i]))

assert (ende_results == ende2_results), "Initialization test 1 failed - got different search results from loading the same index twice"

print "Initialization test 1 passed."

""" Intialization test 2: When index is created with same files as existing index,
resulting index should give same search results as previous one, but should retrieve
the exact same data within the existing index """

start_time = time.clock()
ende3_index = ix.QueryIndex("ende3", "./translate_ende_wmt32k-train-00001-of-00100", "./vocab.ende.32768")
end_time = time.clock()

assert (end_time - start_time > init_time_threshold), "Initialization test 2 failed - took too little time to load an existing index (beyond %d seconds). If this seems too unreasonable for your development environment, please edit the init_time_threshold field in index_tester.py" % (init_time_threshold)

ende3_results = []
for i in range(len(ende_queries)):
	ende3_results.append(ende3_index.searchIndex(ende_queries[i]))

assert (ende_results == ende3_results), "Initialization test 2 failed - two different indexes generated with same files should not give different search results"

print "Initialization test 2 passed."

""" Intialization test 3: When index is created with different files as existing index,
resulting index should not give same search results as previous one """

start_time = time.clock()
ende4_index = ix.QueryIndex("ende4", "./translate_ende_wmt32k-train-00002-of-00100", "./vocab.ende.32768")
end_time = time.clock()

assert (end_time - start_time > init_time_threshold), "Initialization test 3 failed - took too little time to load an existing index (beyond %d seconds). If this seems too unreasonable for your development environment, please edit the init_time_threshold field in index_tester.py" % (init_time_threshold)

ende4_results = []
for i in range(len(ende_queries)):
	ende4_results.append(ende4_index.searchIndex(ende_queries[i]))

assert (ende_results != ende4_results), "Initialization test 3 failed - two different indexes generated with different files should not give exactly identical search results, and this index should not be attempting to pull data from another index on disk"

print "Initialization test 3 passed."

""" Initialization test 4: When index is created with no TFrecords in files matching the corresponding argument, no index should form, and instead an error message will appear in console. However, the program should continue to run."""

blank_index = ix.QueryIndex("blank", "", "./vocab.ende.32768")

print "If you see an error message above, initialization test 4 passed. Otherwise, test failed."

""" Initialization test 5: When index is created with no TFrecord files matching the corresponding argument, it should be blank."""

blank2_index = ix.QueryIndex("blank2", "I'm a dummy!", "./vocab.ende.32768")
blank2_results = []
for i in range(len(ende_queries)):
	blank2_results.append(blank2_index.searchIndex(ende_queries[i]))
blank2_result_lengths = [len(entry) for entry in blank2_results]

for i in range(len(blank2_result_lengths)):
	assert (blank2_result_lengths[i] == 0), "Initialization test 5 for index blank2 failed for entry %d - expected length of 0, not %d" % (i, blank2_result_lengths[i])

""" Initialization test 6: When index is created with a faulty TFrecord file, program should fail and throw a tensorflow.errors.DataLossError exception. """

system_failed = False # True if the system throws an exception creating the index

try:
	error_index = ix.QueryIndex("error", "./dummyfile.txt", "./vocab.ende.32768")
except tf.errors.DataLossError:
	system_failed = True

assert (system_failed), "Initialization test 6 for index error failed"

print "Initialization test 6 passed."

""" Initialization test 7: When index is created without a vocab file, no index should form, and instead an error message will appear in console. However, the program should continue to run."""

blank3_index = ix.QueryIndex("blank3", "./translate_ende_wmt32k-train-00001-of-00100", "")

print "If you see an error message above, initialization test 7 passed. Otherwise, test failed."

""" Initialization test 8: When index is created with a vocab file that is too small, the program should fail and throw an IndexError."""

system_failed = False # True if the system throws an exception creating the index

try:
	error2_index = ix.QueryIndex("error2", "./translate_ende_wmt32k-train-00002-of-00100", "./dummyfile.txt")
except IndexError: 
	system_failed = True

assert (system_failed), "Initialization test 8 for index error2 failed"

print "Initialization test 8 passed."

""" Initialization test 9: When index is created with a vocab file that does not exist, the program should fail."""

system_failed = False # True if the system throws an exception creating the index

try:
	error3_index = ix.QueryIndex("error3", "./translate_ende_wmt32k-train-00002-of-00100", "I'm a dummy!")
except IOError: 
	system_failed = True

assert (system_failed), "Initialization test 9 for index error3 failed"

print "Initialization test 9 passed."

print "All initialization tests finished - please review output."

print "All tests complete. As far as this testing program can tell, QueryIndex's implementation is functionally correct. Please review output to ensure this."
