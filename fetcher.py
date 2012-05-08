import logging
import pymongo
from pymongo import Connection
from requests import async
from time import sleep
import ujson

from loggingutils import basicConfig

basicConfig(console=True)

SEARCH_ENDPOINT = 'http://api.crunchbase.com/v/1/search.js?query=a&page=%s'
COMPANY_ENDPOINT = 'http://api.crunchbase.com/v/1/company/%s.js'

def _get_batch(urls, field=None):
    """
    @param urls: list(str)
    @param field: str
    @return: list(dict)
    """
    try:
        rs = [async.get(u) for u in urls]
        responses = async.map(rs)
        if field:
            results_list = [ujson.decode(r.text)[field] for r in responses]
        else:
            results_list = [ujson.decode(r.text) for r in responses if r.ok]
    except Exception, e:
        logging.exception('exception received.. sleeping it off for 5 sec')
        sleep(5)
        return _get_batch(urls, field)
    return results_list

def fetch_companies(start_idx=1):
    col = Connection()['crunch']['company']

    TOTAL = 8200
    BATCH = 10

    for s in range(start_idx, TOTAL, BATCH):
        print s
        urls = [SEARCH_ENDPOINT % i for i in range(s, s + BATCH)]
        results_list = _get_batch(urls, 'results')
        for results in results_list:
            for result in results:
                data = result
                data['_id'] = result['permalink']
                col.save(data)

def get_companies_list(start_idx=None):
    col = Connection()['crunch']['company']
    query = {}
    if start_idx:
        query['_id'] = {'$gte': start_idx}
    companies = col.find(query, {'_id': 1}).sort([
        ('_id', pymongo.ASCENDING),
        ])
    return companies

def fetch_extended(start_idx=None):
    ext_col = Connection()['crunch']['extended']
    companies = [c['_id'] for c in get_companies_list(start_idx)]

    BATCH = 10

    for s in range(0, len(companies), BATCH):
        print companies[s]
        urls = [COMPANY_ENDPOINT % companies[i] for i in range(s, s + BATCH)]
        results = _get_batch(urls)
        for result in results:
            data = result
            data['_id'] = result['permalink']
            ext_col.save(data)
    print companies


#fetch_companies(2591)
fetch_extended('breakkup-com')
