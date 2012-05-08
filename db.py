from pymongo import Connection
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
        return [c for c in company]

class CountryDB(object):
    def __init__(self, mongo_host):
        self._db = Connection(mongo_host)['crunch']['country']

    def save(self, country):
        self._db.save({'_id':country})

    def increment(self, country):
        self._db.update({'_id':country}, {'$inc': {'c': 1}}, upsert=True)

def main():
    define("console", default=False, type=bool)
    define("mongo_host", default='localhost')

    parse_command_line()
    basicConfig(options=options)
    country_db = CountryDB(options.mongo_host)
    company_db = CompanyDB(options.mongo_host)
    companies = company_db.find({}, fields={'offices': 1}, count=None)
    for company in companies:
        for office in company['offices']:
            country_db.increment(office['country_code'])

if __name__ == "__main__":
    from tornado.options import define
    from tornado.options import parse_command_line
    from tornado.options import options

    from loggingutils import basicConfig
    exit(main())

