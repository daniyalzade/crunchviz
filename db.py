from collections import defaultdict
from datetime import datetime
from pymongo import Connection

from utils.dictutils import get_dotted
from utils.listutils import adv_enumerate

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
                money = multiplier * float(money.replace(suffix, ''))
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
    founded_month = company.get('founded_month')
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

    def find(self, query=None, *args, **kwargs):
        end_ts = datetime(1995, 1, 1)
        query = query or {}
        query['data.founded_at'] = {'$gte': end_ts}
        query['data.category_code'] = {'$ne': None}
        query['data.number_of_employees'] = {'$gt': 0}
        query['data.total_money_raised'] = {'$gt': 0}
        for i in self._db.find(query, *args, **kwargs):
            if get_dotted(i, 'data.founded_at') >= end_ts:
                yield i
        raise StopIteration

COUNTRIES = [
"USA",
"GBR",
"CAN",
"IND",
"DEU",
"FRA",
"AUS",
"ISR",
"ESP",
"CHN",
]
        
def _create_csv(stats_db, company_db):
    stats_cursor = stats_db.find({}, None)
    print 'name,num_countries,funding,funding_capped,days_to_funding,num_rounds,employees,year,category,country'
    for stats in adv_enumerate(stats_cursor, frequency=1000):
        name = stats.get('_id').replace(' ', '_')
        stats = stats['data']
        countries = stats.get('countries')
        country = countries[0] if len(countries) else None
        country = country if country in COUNTRIES else 'other'
        num_rounds = len(stats.get('funding_rounds'))
        founded_at = stats.get('founded_at')
        days_to_funding = 0
        funding_rounds = stats.get('funding_rounds')
        if funding_rounds and funding_rounds[0]['funded_at'] and founded_at.year > 1995:
            days_to_funding = (funding_rounds[0]['funded_at'] - founded_at).days

        funding_capped = min(float(stats.get('total_money_raised')) / 10**6, 100)
        funding = float(stats.get('total_money_raised')) / 10**6
        employees = stats.get('number_of_employees')
        year = founded_at.year
        category = stats.get('category_code')
        try:
            print ','.join(map(lambda k: str(k), [name, len(countries), funding, funding_capped, days_to_funding, num_rounds, employees, year, category, country]))
        except Exception, e:
            pass


def _create_stats(stats_db, company_db):
    companies = company_db.find({},{}, count=None)
    for company in adv_enumerate(companies, frequency=1000):
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
    ##for company in adv_enumerate(companies):
    ##    for office in company['offices']:
    ##        country_db.increment(office['country_code'])
    ##print company_db
    #_create_stats(stats_db, company_db)
    _create_csv(stats_db, company_db)
    return -1
    categories = defaultdict(int)
    year_month = defaultdict(int)
    year = defaultdict(int)
    for stats in adv_enumerate(stats_db.find()):
        categories[get_dotted(stats, 'data.category_code')] += 1
        founded_at = get_dotted(stats, 'data.founded_at') 
        if not founded_at:
            continue
        #if founded_at.year < 1995:
        #    print stats
        year_month[(founded_at.year, founded_at.month)] += 1
        year[founded_at.year] += 1

    print sum(categories.values())
    print year
    print sorted(year_month.items())
    

if __name__ == "__main__":
    from tornado.options import define
    from tornado.options import parse_command_line
    from tornado.options import options

    from loggingutils import basicConfig
    exit(main())

