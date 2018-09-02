import os
import sys
import yaml

import pyjq
import requests

def update_setting():

    with open('config.yaml', "r") as f:
        config = yaml.load(f)
    headers = {'Authorization': 'Bearer ' + config['remo']['token']}
    url = 'https://api.nature.global/1/appliances/{}/aircon_settings'.format(config['remo']['appliance'])
    current = _current(config)
    print('current is')
    print(current)
    req = {'temperature': _inc(current['temp'])}
    print('request is')
    print(req)
    res = requests.post(url, headers=headers, json=req)
    print('response is')
    print(res.status_code)
    print(res.json())

def _current(config):
    headers = {'Authorization': 'Bearer ' + config['remo']['token'], 'accept': 'application/json'}
    url = 'https://api.nature.global/1/appliances'
    res = requests.get(url, headers=headers)
    q = '.[] | select(.id=="{}") | .settings'.format(config['remo']['appliance'])
    return pyjq.first(q, res.json())

def _inc(temp):
    return str(int(temp) + 1)

if __name__ == '__main__':
    update_setting()
