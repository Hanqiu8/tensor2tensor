# coding=utf-8
# Copyright 2017 The Tensor2Tensor Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
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
from whoosh import index, fields, qparser
from whoosh.collectors import TimeLimitCollector, TimeLimit

class QueryIndex:
    """ Creates a QueryIndex object and the associated index file
    to go with it, or if an index file of the desired name already
    exists, creates a QueryIndex object that accesses that file.
    
    Args:
        name - name of the desired index
    """
    def __init__(self, name):
        if not os.path.exists("indexes"):
            os.mkdir("indexes")
        
        self.schema = Schema(query=TEXT(stored=True, unique=True), target=TEXT(stored=True))
        
        if index.exists_in("indexes", indexname=name):
            self.ix = index.open_dir("indexes", indexname)
        else:
            self.ix = index.create_index(self.schema, indexname=name)
    
    """ Adds the query-target pair passed to this method to the
    indexing file this object represents.
    
    If there is already a pair with the passed query in the index,
    that pair is replaced with the one passed to this method.
    
    Note that these query-targer pairs will always be stored as
    Unicode.
    
    Args:
       qry, trgt - the pair in question
    """
    def addPair(self, qry, trgt):
        self.ix.writer.update_document(query=unicode(qry),
                                       target=unicode(trgt))
        self.ix.writer.commit()
    
    """ Returns a list of query-target pairs that match the search
    query passed to this method. This list is limited to the 20
    most related pairs.
    
    Args:
       sq - the search query
    
    TODO: Allow this to return a more robust number and selection
    of results from a query
    """
    def search(self, sq):
        parser = MultifieldParser(["query", "target"], 
                                  schema=self.schema).parse(unicode(sq))
        with self.ix.searcher() as s:
            results = s.search(parser, limit=20)
            return results

"""
this function serves as a temporary dummy funciton and should be replaced.
this function is currently called by server.corpus_search() api request.
"""
def get_result():
    return "TODO: this is a dummy result and should be replaced."
