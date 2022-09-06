from elasticsearch import Elasticsearch
from datetime import datetime
from fastapi import FastAPI

app = FastAPI()

host = 'elasticsearch'
port = 9200
es = Elasticsearch(f'http://{host}:{port}')

@app.get("/")
def home():
    try:
        doc = {
            'author': 'mgurevich',
            'text': 'Hello world!',
            'timestamp': datetime.now(),
        }
        resp = es.index(index="test-index", id=1, document=doc)
        print(resp['result'])

        resp = es.get(index="test-index", id=1)
        print(resp['_source'])

        return resp
    except Exception as e:
        return f'Elastic search error {e}!'