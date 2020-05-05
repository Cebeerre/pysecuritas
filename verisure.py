#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import xmltodict
from datetime import datetime
import time
import json
import argparse
import textwrap
import itertools

DALARM_OPS = {
    'ARM': 'arm all sensors (inside)',
    'ARMDAY': 'arm in day mode (inside)',
    'ARMNIGHT': 'arm in night mode (inside)',
    'PERI': 'arm (only) the perimeter sensors',
    'DARM': 'disarm everything (not the annex)',
    'ARMANNEX': 'arm the secondary alarm',
    'DARMANNEX': 'disarm the secondary alarm',
    'EST': 'return the panel status'
}

DAPI_OPS = {
    'ACT_V2': 'get the activity log',
    'SRV': 'SIM Number and INSTIBS',
    'MYINSTALLATION': 'Sensor IDs and other info'
}

ALARM_OPS = list(DALARM_OPS.keys())
API_OPS = list(DAPI_OPS.keys())
ALL_OPS = dict(itertools.chain(DALARM_OPS.items(), DAPI_OPS.items()))
HELP_OPS = '\n'.join([': '.join(i) for i in ALL_OPS.items()])
PANEL = 'SDVFAST'
TIMEFILTER = '3'


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
        payload.update({'request': action, 'hash': hash, 'ID': id})
        if action in ALARM_OPS:
            payload['request'] = action + '1'
            self.call_verisure_get('GET', payload)
            payload['request'] = action + '2'
            output = self.call_verisure_get('GET', payload)
            res = output['PET']['RES']
            while res != 'OK':
                output = self.call_verisure_get('GET', payload)
                res = output['PET']['RES']
        elif action in API_OPS:
            if action == 'ACT_V2':
                payload.update(
                    {'timefilter': TIMEFILTER, 'activityfilter': '0'})
            output = self.call_verisure_get('GET', payload)
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


def create_args_parser():
    desc = 'Verisure/SecuritasDirect API Client\nhttps://github.com/Cebeerre/VerisureAPIClient'
    parser = argparse.ArgumentParser(
        description=desc, formatter_class=argparse.RawTextHelpFormatter)
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
                        help=textwrap.dedent(HELP_OPS),
                        type=str)
    return parser


def main():
    args = create_args_parser().parse_args()
    client = VerisureAPIClient(args.username, args.password,
                               args.installation, PANEL, args.country, args.language, 1)
    if (args.COMMAND in ALARM_OPS) or (args.COMMAND in API_OPS):
        print(client.operate_alarm(args.COMMAND))


if __name__ == '__main__':
    main()
