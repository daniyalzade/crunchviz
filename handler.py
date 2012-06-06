import os.path
import tornado.web
from tornado import template
import ujson

from db import CompanyDB
from db import StatsDB
from utils.tornado import jsonp
from utils.dictutils import make_jsonable
from utils.dictutils import get_dotted
from utils.dictutils import set_dotted

DB_API_MAP = {
    '_id': 'name',
    'data.number_of_employees': 'numEmployees',
    'data.category_code': 'category',
    'data.founded_at': 'foundedAt',
    'data.total_money_raised': 'funding',
    }
@jsonp
class StatsHandler(tornado.web.RequestHandler):
    def initialize(self, mongo_host=None):
        self._db = StatsDB(mongo_host)
        # Template loader for HTML requests
        self._loader = None

    def _get_html(self, data):
        """
        @param data: dict
        """
        if not self._loader:
            path = os.path.join(os.path.dirname(__file__), 'template')
            self._loader = template.Loader(path)

        context = {'data': data}
        html = self._loader.load("statsview.html").generate(**context)
        self.write(html)
        return

    def get(self):
        count = int(self.get_argument('count', 1000))
        format = self.get_argument('format', 'html')
        human = bool(self.get_argument('human', None))
        data = {}
        stats = []
        stats_cursor = self._db.find({}, None)
        for idx, stat in enumerate(stats_cursor):
            if count and idx > count:
                break
            item = {}
            for k, v in DB_API_MAP.items():
                set_dotted(item, v, get_dotted(stat, k))
            stats.append(item)
        if format == 'html':
            return self._get_html(data)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        data['count'] = len(stats)
        data['stats'] = make_jsonable(stats, human)
        data = ujson.encode(data)
        self.write(data)

@jsonp
class CompanyHandler(tornado.web.RequestHandler):
    def initialize(self, mongo_host=None):
        self._db = CompanyDB(mongo_host)
        # Template loader for HTML requests
        self._loader = None

    def _get_html(self, data):
        """
        @param data: dict
        """
        if not self._loader:
            path = os.path.join(os.path.dirname(__file__), 'template')
            self._loader = template.Loader(path)

        context = data
        html = self._loader.load("listview.html").generate(**context)
        self.write(html)
        return

    def get(self):
        count = int(self.get_argument('count', 10))
        country_code = self.get_argument('country_code', '').upper()
        format = self.get_argument('format', 'html')
        data = {}
        companies = self._db.find({},
                country_code=country_code,
                count=count,
                )
        data['companies'] = companies
        if format == 'html':
            return self._get_html(data)
        self.write(ujson.encode(data))

def main():
    define("console", default=False, type=bool)
    define("mongo_host", default='localhost')

    parse_command_line()
    basicConfig(options=options)
    db = Connection(options.mongo_host)['crunch']['company_stats']

if __name__ == "__main__":
    from tornado.options import define
    from tornado.options import parse_command_line
    from tornado.options import options

    from loggingutils import basicConfig
    from pymongo import Connection

    exit(main())
