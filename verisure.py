#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import xmltodict
from datetime import datetime
import time
import json
import argparse

ALARM_OPS = ('PERI', 'ARM', 'ARMNIGHT', 'ARMDAY',
             'DARM', 'EST', 'ARMANNEX', 'DARMANNEX')


class VerisureAPIClient():
    BASE_URL = 'https://mob2217.securitasdirect.es:12010/WebService/ws.do'

    def __init__(self, user, pwd, numinst, panel, country, lang, rate):
        self.user = user
        self.rate = rate
        self.LOGIN_PAYLOAD = {'Country': country,
                              'user': user, 'pwd': pwd, 'lang': lang}
        self.OP_PAYLOAD = {'Country': country, 'user': user,
                           'pwd': pwd, 'lang': lang, 'panel': panel, 'numinst': numinst}
        self.OUT_PAYLOAD = {'Country': country, 'user': user,
                            'pwd': pwd, 'lang': lang, 'numinst': '(null)'}

    def call_verisure_get(self, method, parameters):
        time.sleep(self.rate)
        if method == 'GET':
            response = requests.get(self.BASE_URL, params=parameters)
        elif method == 'POST':
            response = requests.post(self.BASE_URL, params=parameters)
        if response.status_code == 200:
            output = xmltodict.parse(response.text)
            return output
        else:
            return None

    def op_verisure(self, action, hash, id):
        payload = self.OP_PAYLOAD
        payload.update({'request': action + '1', 'hash': hash, 'ID': id})
        self.call_verisure_get('GET', payload)
        payload['request'] = action + '2'
        output = self.call_verisure_get('GET', payload)
        res = output['PET']['RES']
        while res != 'OK':
            output = self.call_verisure_get('GET', payload)
            res = output['PET']['RES']
        return json.dumps(output, indent=2)

    def generate_id(self):
        ID = 'IPH_________________________' + self.user + \
            datetime.now().strftime("%Y%m%d%H%M%S")
        return ID

    def get_login_hash(self):
        payload = self.LOGIN_PAYLOAD
        payload.update({'request': 'LOGIN', 'ID': self.generate_id()})
        output = self.call_verisure_get('POST', payload)
        return output['PET']['HASH']

    def logout(self, hash):
        payload = self.OUT_PAYLOAD
        payload.update({'request': 'CLS', 'hash': hash,
                        'ID': self.generate_id()})
        output = self.call_verisure_get('GET', payload)
        return json.dumps(output)

    def operate_alarm(self, action):
        hash = self.get_login_hash()
        id = self.generate_id()
        status = self.op_verisure(action, hash, id)
        self.logout(hash)
        return status

    def log(self):
        hash = self.get_login_hash()
        id = self.generate_id()
        payload = self.OP_PAYLOAD
        payload.update({'request': 'ACT_V2', 'hash': hash,
                        'ID': id, 'timefilter': '5', 'activityfilter': '0'})
        output = self.call_verisure_get('GET', payload)
        return json.dumps(output, indent=2)


def create_args_parser():
    desc = 'Verisure/SecuritasDirect API Client\nhttps://github.com/Cebeerre/VerisureAPIClient'
    commands = ', '.join(ALARM_OPS) + ', ACT'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-u',
                        '--username',
                        help='Username used in the web page/mobile app.',
                        required=True)
    parser.add_argument('-p',
                        '--password',
                        help='Password used in the web page/mobile app.',
                        required=True)
    parser.add_argument('-i',
                        '--installation',
                        help='Installation/Facility number (appears on the website).',
                        required=True)
    parser.add_argument('-c',
                        '--country',
                        help='Your country (UPPERCASE): ES, IT, FR, GB, PT ...',
                        required=True)
    parser.add_argument('-l',
                        '--language',
                        help='Your language (lowercase): es, it, fr, en, pt ...',
                        required=True)
    parser.add_argument('COMMAND',
                        help='Your request/command: ' + commands,
                        type=str)
    return parser


def main():
    args = create_args_parser().parse_args()
    client = VerisureAPIClient(args.username, args.password,
                               args.installation, 'SDVFAST', args.country, args.language, 1)
    if args.COMMAND in ALARM_OPS:
        print(client.operate_alarm(args.COMMAND))
    elif args.COMMAND == 'ACT':
        print(client.log())


if __name__ == '__main__':
    main()
