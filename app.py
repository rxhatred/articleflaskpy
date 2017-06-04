#!flask/bin/python
import os
import collections
import pymongo
import sys
import re

reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Flask, render_template
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

app.config['MONGO_DBNAME'] = 'scrapynews'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/scrapynews'

mongo = PyMongo(app)

def query_all():
    articles = mongo.db.articles
    
    results = []
    
    for q in articles.find():
        data = convert(q)
        results.append({'title':data['title'],'author':data['author'],'url':data['url'],'description':clean_text(data['description'])})
    
    return results

def clean_text(html):
    tag_rmvr = re.compile('<.*?>')
    rt = re.sub(tag_rmvr, '', html)
    return rt

@app.route('/')
def index():
    results = query_all()
        
    return render_template('index.html', out = results)

@app.route('/all')
def get_all():
    results = query_all()
        
    return jsonify(results)
    
@app.route('/getbyarticlename/<title>', methods=['GET'])
def get_by_articlename(title):
    articles = mongo.db.articles
    
    rgx = re.compile('^'+title, re.IGNORECASE)
    data = articles.find_one({'title':rgx});
    if data:
        result = {'title':data['title'],'author':data['author'],'url':data['url'],'description':data['description']}
    else:
        result = {'results':'No record found'}
    
    return jsonify(result)
    
if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))
