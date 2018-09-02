import json
import yaml
import pyjq

with open('remo.json', "r") as f:
    d = json.load(f)
with open('config.yaml', "r") as f:
    config = yaml.load(f)
q = '.[] | select(.id=="{}") | .settings'.format(config['remo']['appliance'])
x = pyjq.first(q, d)
print(x['temp'])
print('end')
