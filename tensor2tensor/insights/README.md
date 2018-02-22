# Tensor2Tensor Insights

The Insights packages provides an interactive webservice for understanding the
inner workings of a Tensor2Tensor model.  It will provide a series of
visualizations extracted from a requested T2T model that informs model developers
and model users on how to improve or best utilize a model.

## Dependencies

Before using the Insights server, you must install [Bower](https://bower.io/)
which we use to manage our web component dependencies.  You can easily install
this with the [Node Package Manager](https://www.npmjs.com/).

## Setup Instructions

After training a model, such as according to the Quick Start guide, you can run
the `t2t-insights-server` binary and begin querying it.

First, prepare the bower dependencies by navigating into the
`tensor2tensor/insights/polymer` directory and running `bower install`:

```
pushd tensor2tensor/insights/polymer
bower install
popd
```

The models run by server is then configured by a JSON version of the
InsightsConfiguration protocol buffer.  For instance, a sample configuration
for the translate_ende_wmt32k problem would be:

```
{
  "configuration": [{
    "source_language": "en",
    "target_language": "de",
    "label": "translate_ende",
    "transformer": {
      "model": "transformer",
      "model_dir": <path to the folder containing the full model>,
      "data_dir": <path to the data in question. For the translate_ende_wmt32k problem, this directory should hold the vocab.ende.32768 file>,
      "hparams": "",
      "hparams_set": "transformer_base_single_gpu",
      "problems": "translate_ende_wmt32k"
    }
  }],
 "language": [{
    "code": "en",
    "name": "English"
  },{
    "code": "de",
    "name": "German"
  }],
  "source_language_data_file": <path to data file with source language words/sentences>,
  "target_language_data_file": <path to data file with target language words/sentences>
}
```

Replace the angle brackets with a string containing what is correct for you. 
source_language_data_file and target_language_data_file allow you to use the 
corpus search functionality. If this functionality is not required, simply 
set the values to "".

With that saved to `configuration.json`, run the following, again substituting
anything in angle brackets:

```
t2t-insights-server \
  --configuration=<path to configuration.json> \
  --static_path=<a static path to tensor2tensor/insights/polymer. The quickest way to do this is to substitute this field with `pwd` and run this command within the polymer directory itself>
```

This will bring up a minimal [Flask](http://flask.pocoo.org/) REST service
served by a [GUnicorn](http://gunicorn.org/) HTTP Server.

## Corpus Search
To see which training data might be associated with a given query, you can use
the corpus search functionality. In the configuration.json, provide 2 files with
the training data from the source and target languages. On the first query,
an index of the training data will be created and saved in an "indexes" folder,
wherever the tensor2tensor-insights-server command is being run. This may require
tensor2tensor-insights-server to be run with sudo. As long as the "indexes" folder
is not removed, this index will be used automatically in future runtimes of the 
server, and will not need to be recreated.

## Features to be developed

This is a minimal web server.  We are in the process of adding additional
exciting features that give insight into a model's behavior:

  * Integrating a multi-head attention visualization.
  * Registering multiple models to compare their behavior.
  * Indexing training data to find examples related to a current query.
  * Tracking interesting query + translation pairs for deeper analysis.
