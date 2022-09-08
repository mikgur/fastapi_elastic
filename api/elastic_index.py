import os
from elasticsearch import Elasticsearch
import json
import time
import logging

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

    num_tries = 0
    index_loaded = False
    while not index_loaded:
        try:
            # print(f'Trying {num_tries}')
            logging.info(f'Loading elasticsearch index attempt #{num_tries}')
            es.bulk(index="clinvar", operations=actions)
            # print('Success!!!')
            logging.info(f'Elasticsearch index loaded successfully!')
            index_loaded = True
        except Exception as e:
            # print(f'Failed {num_tries}')
            logging.info(f'Loading elasticsearch index attempt #{num_tries} failed')
            if num_tries > 4:
                raise e
            num_tries += 1
            time.sleep(10)
    return es