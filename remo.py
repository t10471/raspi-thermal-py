import logging
import yaml

import pyjq
import requests
import numpy as np

class RemoFactory:

    @staticmethod
    def create(config, fname):
        return Remo(fname) if config['use_remo'] else DummyRemo(fname)

class DummyRemo:

    def __init__(self, fname):
        pass

    def update(self, pixels):
        pass

class Remo:

    def __init__(self, fname):
        with open(fname, "r") as f:
            self.config = yaml.load(f)['remo']
        self.min = self.config['min']
        self.max = self.config['max']
        self.margin = self.config['margin']
        self.pre = None

    def update(self, pixels):
        if self.pre is None:
            self.pre = np.array(pixels)
            return
        self.current = self._current()
        self._make_request(pixels).request(self.current)

    def _current(self):
        headers = {'Authorization': 'Bearer ' + self.config['token'], 'accept': 'application/json'}
        url = 'https://api.nature.global/1/appliances'
        res = requests.get(url, headers=headers)
        q = '.[] | select(.id=="{}") | .settings'.format(self.config['appliance'])
        return int(pyjq.first(q, res.json())['temp'])

    def _make_request(self, pixels):
        if self.current >= self.max or self.current <= self.min:
            return DummyRequest(self.config)
        c = np.average(np.array(pixels))
        p = np.average(np.array(self.pre))
        x = p - c
        if x <= self.margin:
            return DummyRequest(self.config)
        elif x < 0.0:
            return IncRequest(self.config)
        else:
            return DecRequest(self.config)

class RequestBuilder:

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('Thermal').getChild('Remo')

    def request(self, req):
        self.logger.debug(req)
        headers = {'Authorization': 'Bearer ' + self.config['token']}
        url = 'https://api.nature.global/1/appliances/{}/aircon_settings'.format(self.config['appliance'])
        res = requests.post(url, headers=headers, json=req)
        self.logger.debug('response is {}'.format(res.status_code))
        self.logger.debug(res.json())
        self.logger.info('update {}'.format(req))

class DummyRequest:

    def __init__(self, config):
        pass

    def request(self, current):
        logger = logging.getLogger('Thermal').getChild('Remo')
        logger.info('not update {}'.format(current))

class IncRequest:

    def __init__(self, config):
        self.executer = RequestBuilder(config)

    def request(self, current):
        self.executer.request({'temperature': str(current + 1)})

class DecRequest:

    def __init__(self, config):
        self.executer = RequestBuilder(config)

    def request(self, current):
        self.executer.request({'temperature': str(current - 1)})
