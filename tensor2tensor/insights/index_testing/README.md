## Tensor2Tensor Indexing Testing

This directory holds data and test cases for the `QueryIndex` class in `insights/indexing.py`. It tests for functional correctness, including the behavior of its interface, the creation of search indexes, and the searching of index entries. These fulfill the requirements demanded for this project.s

## Dependencies

You must install [Whoosh](https://pypi.python.org/pypi/Whoosh/), which can be achieved by `pip install whoosh`

## Setup Instructions

First, use the Quick Start guide and the `t2t-datagen` binary to generate
data files for the `translate_ende_wmt32k` problem and move them to this
directory.

Depending on the performance of your development environment, you may need
to open `index_tester.py` and change the `init_time_threshold` field to a
value that better suits your setup. This is especially true for setups with
higher processing power.

Once you've done that, simply run `python index_tester.py`
