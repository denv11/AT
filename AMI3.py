#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
from panoramisk import Manager
import threading, queue
import requests, json
import pickle
import re, os

# API метод CRM
# url = 'https://crm-name.ru/call'

# данные для доступа к AMI
ip = '10.10.11.101'
prt = '5038'
username =  'test'
secret = 'Cd12345678_er'


manager = Manager(host=ip,
                  port=prt,
                  username=username,
                  secret=secret)


# меня интересуют только записи cdr
#@manager.register_event()
def callback(event, manager):
#    r = re.compile(".*from-did-direct.*")
    if "FullyBooted" not in manager.event:
        info = dict(manager)
#       if filter(r.match, os.__dict__.values()):
        print(info)
        # код для отправки post запроса на удаленный сервер
#    url = 'https://SITE/scan/cdr.php'
#    headers = {'content-type': 'application/json', 'Accept': 'text/plain'}
#    r = requests.post(url, data=json.dumps(info_cdr), headers=headers)


def main():
    manager.connect()
    try:
        manager.loop.run_forever()
    except KeyboardInterrupt:
        manager.loop.close()


if __name__ == '__main__':
    main()