from datetime import datetime
from pymongo import Connection

from utils.dictutils import get_dotted
from utils.dictutils import set_dotted
from utils.listutils import iterate_with_progress

class CompanyDB(object):
    def __init__(self, mongo_host):
        self._db = Connection(mongo_host)['crunch']['extended']

    def find(self, query,
            country_code=None,
            fields=None,
            count=10,
            ):
        """
        @param query: dict
        @param count: int
        @return: list(dict)
        """
        fields = fields or None
        if country_code:
            query['offices'] = {
                    '$elemMatch': {'country_code':country_code},
                    }
        company = self._db.find(query, fields)
        if count:
            company.limit(count)
        return company

class CountryDB(object):
    def __init__(self, mongo_host):
        self._db = Connection(mongo_host)['crunch']['country']

    def save(self, country):
        self._db.save({'_id':country})

    def increment(self, country):
        self._db.update({'_id':country}, {'$inc': {'c': 1}}, upsert=True)

money_types = [
        (10**9, 'b'),
        (10**6, 'm'),
        (10**3, 'k'),
        ]
def _parse_money(money):
    try:
        money = money.replace('$', '')
        return int(money)
    except ValueError:
        for multiplier, suffix in money_types:
            try:
                money = multiplier * float(money.replace(suffix, ''))
                return money
            except ValueError:
                pass
    return None

def _get_money_raised(company):
    money = company.get('total_money_raised', '').lower()
    if not money:
        return 0
    try:
        money = money.replace('$', '')
        money = int(money)
    except ValueError:
        for multiplier, suffix in money_types:
            try:
                money = multiplier * int(money.replace(suffix, ''))
                return ('total_money_raised', money)
            except ValueError:
                pass
    return ('total_money_raised', money)

def _get_funding_rounds(company):
    funding_rounds = company.get('funding_rounds', [])
    def _get_funding_round(funding_round):
        amount = funding_round['raised_amount']
        funding_year = funding_round['funded_year']
        funding_month = funding_round['funded_month']
        funded_at = _get_datetime(funding_year, funding_month)
        return {'funded_at': funded_at, 'amount': amount}

    return ('funding_rounds', [_get_funding_round(f) for f in funding_rounds])

def _get_datetime(year, month):
    ts = None
    if year and not month:
        ts = datetime(int(year), 1, 1)
    elif year and month:
        ts = datetime(int(year), int(month), 1)
    return ts

def _get_founded_at(company):
    founded_year = company.get('founded_year')
    founded_month = company.get('founded_moth')
    founded_at = _get_datetime(founded_year, founded_month)
    return ('founded_at', founded_at)

def _get_category_code(company):
    category_code = company.get('category_code', '')
    return ('category_code', category_code)

def _get_tag_list(company):
    tag_list = company.get('tag_list', [])
    return ('tag_list', tag_list.split(',') if tag_list else [])

def _get_number_of_employees(company):
    return ('number_of_employees', company.get('number_of_employees', None))

STATS = [
        _get_money_raised,
        _get_category_code,
        _get_tag_list,
        _get_founded_at,
        _get_funding_rounds,
        _get_number_of_employees,
        ]

class StatsDB(object):
    def __init__(self, mongo_host):
        self._db = Connection(mongo_host)['crunch']['company_stats']

    def save(self, company, stats):
        self._db.save({'_id':company, 'data': stats})

    def find(self, *args, **kwargs):
        return self._db.find(*args, **kwargs)

def _create_stats(stats_db, company_db):
    companies = company_db.find({},{}, count=None)
    for company in iterate_with_progress(companies):
        stats = {}
        name = company.get('name')
        countries = []
        for office in company['offices']:
            countries.append(office['country_code'])
        stats['countries'] = countries
        for fn in STATS:
            stat_name, val = fn(company)
            stats[stat_name] = val
        stats_db.save(name, stats)

def main():
    define("console", default=False, type=bool)
    define("mongo_host", default='localhost')

    parse_command_line()
    basicConfig(options=options)
    country_db = CountryDB(options.mongo_host)
    company_db = CompanyDB(options.mongo_host)
    stats_db = StatsDB(options.mongo_host)
    #companies = company_db.find({}, fields={'offices': 1}, count=None)
    ##for company in iterate_with_progress(companies):
    ##    for office in company['offices']:
    ##        country_db.increment(office['country_code'])
    ##print company_db
    _create_stats(stats_db, company_db)

    print _parse_money('1.7m')

if __name__ == "__main__":
    from tornado.options import define
    from tornado.options import parse_command_line
    from tornado.options import options

    from loggingutils import basicConfig
    exit(main())

