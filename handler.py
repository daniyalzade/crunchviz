import os.path
import tornado.web
from tornado import template
import ujson

from db import CompanyDB
from utils.tornado import jsonp

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
