import logging
import re
from collections import defaultdict
from itertools import chain, cycle
from json import JSONDecodeError
from operator import methodcaller
from urllib.parse import SplitResult, urlunsplit

import requests

logger = logging.getLogger(__name__)


class ClientBase:
    def __init__(self, definition_url=None):
        if definition_url is None:
            definition_url = 'http://localhost:1234/v1/swagger.json'

        self.session = requests.Session()

        resp = self.session.get(definition_url)

        resp.raise_for_status()

        self.definitions = resp.json()

        self._operations = self._get_operations()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def __getattr__(self, item):
        try:
            path, method = self._operations[item]
            details = self.definitions['paths'][path][method]

            api_call = getattr(self.session, method.lower())

            def operation(**kwargs):
                if not details['parameters']:
                    resp = api_call(self.get_url(path))
                else:
                    args = defaultdict(dict)

                    for p in details['parameters']:
                        name = p['name']
                        if p['required'] and name not in kwargs:
                            raise TypeError("missing required argument '{}': {}".format(name, p['description']))

                        try:
                            value = kwargs.pop(name)

                            if p['in'] == 'body':
                                args['body'] = value
                            else:
                                args[p['in']][name] = value
                        except KeyError:
                            pass

                    if kwargs:
                        raise TypeError("'{}' does not apply to this function".format("', '".join(kwargs.keys())))

                    resp = api_call(self.get_url(path).format(**args['path']), params=args['query'], json=args['body'])

                try:
                    resp.raise_for_status()
                except requests.HTTPError:
                    logger.error(resp.text)
                    raise

                try:
                    return resp.json()
                except JSONDecodeError:
                    return resp.text

            operation.__doc__ = self.generate_method_doc(details)
            operation.__name__ = item

            return operation
        except KeyError:
            raise AttributeError(item)

    @property
    def swagger_version(self):
        return tuple(map(int, self.definitions['swagger'].split('.')))

    def get_url(self, path):
        scheme = 'https' if 'https' in self.definitions['schemes'] else self.definitions['schemes'][0]  # prefer https

        return urlunsplit(SplitResult(
            scheme=scheme,
            netloc=self.definitions['host'],
            path=path,
            query=None,
            fragment=None))

    def _get_operations(self):
        operations = {}

        for path, ops in self.definitions['paths'].items():
            for method, req in ops.items():
                op_id = self.camel_case(req['operationId'])

                operations[op_id] = (path, method)

        return operations

    @property
    def operations(self):
        """
        Get a list of all operations.
        :return:
        """
        return sorted(self._operations.keys())

    @staticmethod
    def generate_method_doc(details):
        return details['description'] + '\n\n' + 'Parameters:\n' + '\n'.join(
            '{} {}: {}'.format(p['name'], '(required)' if p['required'] else '(optional)', p.get('description'))
            for p in details['parameters'])

    @staticmethod
    def camel_case(s):
        return ''.join(a(b) for a, b in
                       zip(chain((lambda x: x[:1].lower() + x[1:],),
                                 cycle((methodcaller('capitalize'),))),
                           filter(None, re.split(r'[^a-zA-Z0-9]+', s))))
