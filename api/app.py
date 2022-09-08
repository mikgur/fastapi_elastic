from elasticsearch import Elasticsearch
from datetime import datetime
from fastapi import FastAPI
import json
import os

app = FastAPI()

host = 'elasticsearch'
port = 9200
es = Elasticsearch(f'http://{host}:{port}')
clinvar_dir = os.path.join(os.path.dirname(__file__), 'data/clinvar_filtered.json')
with open(clinvar_dir, 'r') as file:
    clinvar = json.load(file)
i = 1
for row in clinvar:
    resp = es.index(index="clinvar", id=i, document=row)
    i += 1

@app.get("/")
def home():
    try:
        return 'DeeploId API'
    except Exception as e:
        return f'Elastic search error {e}!'

@app.get("/items/by/id/")
def get_by_keyword(id : int):
    try:
        resp = es.get(index='clinvar', id=id)
        return resp
    except Exception as e:
        return f'Elastic search error {e}!'

@app.get("/items/by/keyword/")
def get_by_keyword(keyword: str):
    try:
        if es is not None:
            search_object = {'match': {'clndn': f'*{keyword}*'}}
            res = es.search(index="clinvar", query=search_object, size=1000)
            return res
    except Exception as e:
        return f'Elastic search error {e}!'

@app.get("/items/by/rs/")
def get_by_rs(rs: str):
    try:
        if es is not None:
            search_object = {'match': {'rs_id': rs}}
            res = es.search(index="clinvar", query=search_object, size=1000)
            return res
    except Exception as e:
        return f'Elastic search error {e}!'