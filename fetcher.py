import logging
from pymongo import Connection
from requests import async
from time import sleep
import ujson

from loggingutils import basicConfig

basicConfig(console=True)

def _get_batch(urls):
    """
    @param urls: list(str)
    @return: list(dict)
    """
    try:
        rs = [async.get(u) for u in urls]
        responses = async.map(rs)
        results_list = [ujson.decode(r.text)['results'] for r in responses]
    except Exception, e:
        logging.exception('exception received.. sleeping it off for 5 sec')
        sleep(5)
        return _get_batch(urls)
    return results_list

def fetch_companies(start_idx=1):
    col = Connection()['crunch']['company']

    TOTAL = 8200
    BATCH = 10
    API_ENDPOINT = 'http://api.crunchbase.com/v/1/search.js?query=a&page=%s'

    for s in range(start_idx, TOTAL, BATCH):
        print s
        urls = [API_ENDPOINT % i for i in range(s, s + BATCH)]
        results_list = _get_batch(urls)
        for results in results_list:
            for result in results:
                data = result
                data['_id'] = result['permalink']
                col.save(data)

fetch_companies(2591)
