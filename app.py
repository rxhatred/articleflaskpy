#!flask/bin/python
import os
import collections
import pymongo
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Flask
from flask import jsonify
from flask import request

from pymongo import MongoClient
from flask_pymongo import PyMongo 

def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert,data))
    else:
        return data

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'bbc'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/bbc'

mongo = PyMongo(app)

@app.route('/')
def index():
    articles = mongo.db.articles
    
    results = []
    
    for q in articles.find():
        data = convert(q)
        results.append({'title':data['title'],'author':data['author'],'url':data['url'],'description':data['description']})
        
    return jsonify(results)
    
if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))
