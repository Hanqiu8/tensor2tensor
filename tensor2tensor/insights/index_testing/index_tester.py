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

""" First, create the indexes to be used for search tests, and search on them """

""" English to German index - Fairly large index, a few characters are unique to German """
ende_index = ix.QueryIndex("ende", "europarl-v7.de-en.de", "europarl-v7.de-en.en")
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
									
""" Search test 2: searchIndex returns ALL entries that satisfy the query """

ende_exp_lengths = [29, 2261, 5851, 23, 3, 31, 0, 0, 0] # target lengths, obtained from alternative parsing
ende_actual_lengths = [len(entry) for entry in ende_results]

for i in range(len(ende_exp_lengths)):
	assert (i < len(ende_actual_lengths) and
	        ende_exp_lengths[i] == ende_actual_lengths[i]), "Search test 2 query %d for index ende failed (expected %d but got %d)" % (i, ende_exp_lengths[i], ende_actual_lengths[i])
		
""" Search test 3: searchIndex entries are returned in order of ascending distance from query"""

for i in range(len(ende_results)):
	for j in range(len(ende_results[i])):
		assert (j == 0 or
				ende_results[i][j]["distance"] >= ende_results[i][j-1]["distance"]), "Search test 3 query %d for index ende failed for entry %d" % (i, j)

print "All search tests passed."

print "All tests complete. QueryIndex's implementation is functionally correct."
