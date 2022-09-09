import os
from elasticsearch import Elasticsearch
import json
import time
import logging

MAX_ATTEMPTS = 10
ATTEMPT_TIMEOUT = 20

def get_elastic_ready(host, port):
    es = Elasticsearch(f'http://{host}:{port}')

    clinvar_dir = os.path.join(os.path.dirname(__file__), 'data/clinvar_filtered.json')
    with open(clinvar_dir, 'r') as file:
        clinvar = json.load(file)

    actions = []
    for i, row in enumerate(clinvar):
        action = {"index": {"_index": "clinvar", "_id": i}}
        actions.append(action)
        actions.append(row)

    attempt_n = 1
    index_loaded = False
    while not index_loaded:
        try:
            logging.info(f'Loading elasticsearch index attempt #{attempt_n}')
            es.bulk(index="clinvar", operations=actions)
            # print('Success!!!')
            logging.info(f'Elasticsearch index loaded successfully!')
            index_loaded = True
        except Exception as e:
            logging.info(f'Loading elasticsearch index attempt #{attempt_n} failed')
            if attempt_n > MAX_ATTEMPTS:
                raise e
            attempt_n += 1
            time.sleep(ATTEMPT_TIMEOUT)
    return es