from __future__ import print_function

import os
import json
import pickle
from io import StringIO
import sys
import signal
import traceback
import numpy as np

import flask

import pandas as pd

import requests

prefix = '/opt/ml/'
model_path = os.path.join(prefix, 'model')

graph_url = os.environ['GRAPH_URL']
dkn_url = os.environ['DKN_URL']

# graph = kg.Kg('kg')
# model = encoding.encoding(graph)

# A singleton for holding the model. This simply loads the model and holds it.
# It has a predict function that does a prediction based on the model and the input data.


class ScoringService(object):
    import kg
    import encoding
    graph = kg.Kg('kg')  # Where we keep the model when it's loaded
    model = encoding.encoding(graph)

    @classmethod
    def get_model(cls):
        """Get the model object for this instance, loading it if it's not already loaded."""
        if cls.model == None:
            # import kg
            # import encoding
            cls.model = model
            # with open(os.path.join(model_path, 'decision-tree-model.pkl'), 'r') as inp:
            #     cls.model = pickle.load(inp)
        return cls.model

    @classmethod
    def predict(cls, input):
        """For the input, do the predictions and return them.

        Args:
            input (a pandas dataframe): The data on which to do the predictions. There will be
                one prediction per row in the dataframe"""
        clf = cls.get_model()
        return clf[input]


# The flask app for serving predictions
app = flask.Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy. In this sample container, we declare
    it healthy if we can load the model successfully."""
    # health = ScoringService.get_model() is not None  # You can insert a health check here

    # status = 200 if health else 404
    status = 200
    return flask.Response(response='\n',
                          status=status,
                          mimetype='application/json')


@app.route('/invocations', methods=['POST'])
def transformation():
    """Do an inference on a single batch of data. In this sample server, we take data as CSV, convert
    it to a pandas data frame for internal use and then convert the predictions back to CSV (which really
    just means one prediction per line, since there's a single column.
    """
    data = None

    # Convert from CSV to pandas
    if flask.request.content_type == 'application/json':
        print("raw data is {}".format(flask.request.data))
        data = flask.request.data.decode('utf-8')
        print("data is {}".format(data))
        data = json.loads(data)
        #data = data['instance']
        print("final data is {}".format(data))
        #s = StringIO(data)
        #print("test!! recieve text is {}".format(s))
        #data = s
        # data = pd.read_csv(s, header=None)
    else:
        return flask.Response(response='This predictor only supports CSV data',
                              status=415,
                              mimetype='text/plain')

    # print('Invoked with {} records'.format(data.shape[0]))
    '''
    input：
    {
        “recall”:[{“id”:1234,”title”:”中国银行”},{“id”:3434,”title”:”中兴进入美国市场”}],
        “history”:[{“id”:5555,”title”:”中国银行收紧银根”},{“id”:3334,”title”:”股市低迷”}]
    }
    output:
    {
    “result”:[{“id”:5555,”score”:0.23},{“id”:3334,”score”:0.11}]
    }
    '''

    history = []
    for i in data['history']:
        print(i['title'])
        history.append(i['title'])
    print(history)

    graph_url = 'http://54.87.130.9:8080/invocations'  #history urll ???
    header = {'Content-Type': 'application/json'}
    his_data = {'instance': history}
    his_res = requests.post(graph_url, params=his_data, headers=header)

    recall = []
    for i in data['recall']:
        print(i['title'])
        recall.append(i['title'])
    print(recall)

    #graph_url=graph_url='http://54.87.130.9:8080/invocations' #recall urll ???
    header = {'Content-Type': 'application/json'}
    recall_data = {'instance': recall}
    recall_res = requests.post(graph_url, params=recall_data, headers=header)

    #build click_entities
    click_entities = []
    for i in his_res:
        print(i[1])
        click_entities.append(i[1])
    print(click_entities)

    #build click_words
    click_words = []
    for i in his_res:
        print(i[0])
        click_words.append(i[0])
    print(click_words)

    instances = []
    for i in recall_res:
        news_words = i[0]
        news_entities = i[1]
        instance = {
            "news_words": news_words,
            "news_entities": news_entities,
            "click_words": click_words,
            "click_entities": click_entities
        }
        instances.append(instance)
    dkn_data = {"signature_name": "serving_default", "instances": instances}
    print(dkn_data)

    #dkn_url='https://api.ireaderm.net/account/charge/info/android' #dkn urll ???
    header = {'Content-Type': 'application/json'}
    dkn_res = requests.post(dkn_url, params=dkn_data, headers=header)

    results = []
    for i in range(len(data['recall'])):
        result = {
            "id": data['recall'][i]["id"],
            "score": dkn_res['predictions'][i]
        }
        results.append(result)
    response = {"result": results}

    return flask.Response(response=response, status=200, mimetype='application/json')

    # Do the prediction
    #predictions = ScoringService.predict(data)
    #print("prediction is {}".format(predictions))

    ## Convert from numpy back to CSV
    #out = StringIO.StringIO()
    #pd.DataFrame({'results':predictions}).to_csv(out, header=False, index=False)
    #result = out.getvalue()
    #rr = json.dumps({'result': np.asarray(predictions).tolist()})
    """
    rr = data
    print("bytes prediction is {}".format(rr))

    return flask.Response(response=rr, status=200, mimetype='application/json')
    """
