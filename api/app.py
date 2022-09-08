from elastic_index import get_elastic_ready
from fastapi import FastAPI
import logging

LOGGING_CONFIG = {
    'version': 1,
    'loggers': {
        '': {  # root logger
            'level': 'INFO',
            'handlers': ['debug_console_handler'],
        }
    },
    'handlers': {
        'debug_console_handler': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        }
    },
    'formatters': {
        'info': {
            'format': '%(asctime)s-%(levelname)s-%(name)s::%(module)s|%(lineno)s:: %(message)s'
        }
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

app = FastAPI()

host = 'elasticsearch'
port = 9200

es = get_elastic_ready(host, port)

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
