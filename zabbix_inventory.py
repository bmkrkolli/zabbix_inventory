#!/usr/bin/env python

from __future__ import print_function
import requests
import json

url = 'http://<ip>/api_jsonrpc.php'
payload = '{"jsonrpc": "2.0", "method": "host.get", "params": {"output": ["hostid","host","name","status"],"selectInventory": ["os_full","tag"]}, "auth": "<token>", "id": 1 }'
headers = {'content-type': 'application/json-rpc'}
r = requests.post(url, data=payload, headers=headers)

hostslist = r.json()['result']
inventory = {'_meta': {'hostvars': {}}}

for item in hostslist:
   hid = item['hostid']
   ipl = '{"jsonrpc": "2.0", "method": "hostinterface.get", "params": { "output": ["ip"], "hostids": "' + hid + '"}, "auth": "<token>", "id": 1 }'
   ri = requests.post(url, data=ipl, headers=headers)
   for i in ri.json()['result']: 
      item['ip'] = i['ip']

   if item['status'] == '0':
      if item['inventory']:
         hostname = item['host']
         hostvars = dict()

         if item['inventory']['tag'] == 'linux':
            groupname = 'linux'
         if item['inventory']['tag'] == 'windows':
            groupname = 'windows'
            
         if groupname not in inventory:
            inventory[groupname] = {'hosts':[],'vars':{}}

         if item['inventory']['tag'] == 'linux':
            inventory[groupname]['vars']['ansible_python_interpreter'] = '/usr/bin/python3'
         if item['inventory']['tag'] == 'windows':
            inventory[groupname]['vars'] = {'ansible_connection': 'winrm', 'ansible_port': '5985', 'ansible_winrm_transport': 'basic'}

         inventory[groupname]['hosts'].append(hostname)
        
         hostvars['ansible_host'] = item['ip']

         inventory['_meta']['hostvars'][hostname] = hostvars

print(json.dumps(inventory, indent=2))
