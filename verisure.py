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
import base64


class VerisureAPIClient():
    BASE_URL = 'https://mob2217.securitasdirect.es:12010/WebService/ws.do'
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
    DALARM_OPS = {
        'ARM': 'arm all sensors (inside)',
        'ARMDAY': 'arm in day mode (inside)',
        'ARMNIGHT': 'arm in night mode (inside)',
        'PERI': 'arm (only) the perimeter sensors',
        'DARM': 'disarm everything (not the annex)',
        'ARMANNEX': 'arm the secondary alarm',
        'DARMANNEX': 'disarm the secondary alarm',
        'EST': 'return the panel status',
        'IMG': 'Take a picture (requires -s)'
    }
    DAPI_OPS = {
        'ACT_V2': 'get the activity log',
        'SRV': 'SIM Number and INSTIBS',
        'MYINSTALLATION': 'Sensor IDs and other info'
    }
    PANEL = 'SDVFAST'
    TIMEFILTER = '3'
    RATELIMIT = 1
    ALARM_OPS = list(DALARM_OPS.keys())
    API_OPS = list(DAPI_OPS.keys())

    def __init__(self, **args):
        self.user = args.get('username')
        self.sensor = args.get('sensor')
        self.LOGIN_PAYLOAD = {'Country': args.get('country'),
                              'user': args.get('username'), 'pwd': args.get('password'), 'lang': args.get('language')}
        self.OP_PAYLOAD = {'Country': args.get('country'), 'user': args.get('username'),
                           'pwd': args.get('password'), 'lang': args.get('language'), 'panel': self.PANEL, 'numinst': args.get('installation')}
        self.OUT_PAYLOAD = {'Country': args.get('country'), 'user': args.get('username'),
                            'pwd': args.get('password'), 'lang': args.get('language'), 'numinst': '(null)'}

    def return_commands(self):
        all_ops = dict(itertools.chain(
            self.DALARM_OPS.items(), self.DAPI_OPS.items()))
        return all_ops

    def call_verisure_get(self, method, parameters):
        time.sleep(self.RATELIMIT)
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
        if action == 'IMG':
            payload.update(
                {'device': self.sensor, 'instibs': self.instibs, 'idservice': '1'})
        if action == 'INF':
            payload.update({'idsignal': self.idsignal,
                            'signaltype': self.signaltype})
        if action in self.ALARM_OPS:
            payload['request'] = action + '1'
            self.call_verisure_get('GET', payload)
            payload['request'] = action + '2'
            output = self.call_verisure_get('GET', payload)
            res = output['PET']['RES']
            while res != 'OK':
                output = self.call_verisure_get('GET', payload)
                res = output['PET']['RES']
        elif (action in self.API_OPS) or (action == 'INF'):
            if action == 'ACT_V2':
                payload.update(
                    {'timefilter': self.TIMEFILTER, 'activityfilter': '0'})
            output = self.call_verisure_get('GET', payload)
        clean_output = output['PET']
        del clean_output['BLOQ']
        return clean_output

    def generate_id(self):
        ID = 'IPH_________________________' + self.user + \
            datetime.now().strftime('%Y%m%d%H%M%S')
        return ID

    def get_login_hash(self):
        payload = self.LOGIN_PAYLOAD
        payload.update({'request': 'LOGIN', 'ID': self.generate_id()})
        output = self.call_verisure_get('POST', payload)
        if output['PET']['RES'] == 'OK':
            return output['PET']['HASH']
        else:
            return output

    def logout(self, hash):
        payload = self.OUT_PAYLOAD
        payload.update({'request': 'CLS', 'hash': hash,
                        'ID': self.generate_id()})
        output = self.call_verisure_get('GET', payload)
        return None

    def operate_alarm(self, action):
        if (action in self.ALARM_OPS) or (action in self.API_OPS):
            hash = self.get_login_hash()
            if type(hash) is list:
                return hash
            id = self.generate_id()
            if (action == 'IMG'):
                if self.sensor == None:
                    status = {'RES': 'KO', 'MSG': 'Missing Sensor ID'}
                    return status
                self.instibs = self.op_verisure('SRV', hash, id)[
                    'INSTALATION']['INSTIBS']
                self.op_verisure(action, hash, id)
                self.signaltype = '0'
                while self.signaltype != '16':
                    time.sleep(self.RATELIMIT)
                    log = self.op_verisure('ACT_V2', hash, id)[
                        'LIST']['REG'][0]
                    self.idsignal = log['@idsignal']
                    self.signaltype = log['@signaltype']
                output = self.op_verisure('INF', hash, id)
                files = {}
                for i in range(1, 4):
                    filename = datetime.now().strftime('%Y%m%d%H%M%S') + '_' + str(i) + '.jpg'
                    key = 'IMG' + str(i)
                    files.update({key: filename})
                    f = open(filename, 'wb')
                    f.write(base64.b64decode(
                        output['DEVICES']['DEVICE']['IMG'][i - 1]['#text']))
                    f.close()
                    status = {'RES': 'OK', 'MSG': 'Images written to disk.'}
                    status.update({'FILES': files})
            else:
                status = self.op_verisure(action, hash, id)
            self.logout(hash)
            return status
        else:
            status = {'RES': 'KO', 'MSG': 'Invalid command.'}
            return status


def create_args_parser(help_cmd):
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
    parser.add_argument('-s',
                        '--sensor',
                        help='The sensor ID (to take a picture using IMG)',
                        required=None)
    parser.add_argument('COMMAND',
                        help=textwrap.dedent(help_cmd),
                        type=str)
    return parser


def main():
    commands = VerisureAPIClient().return_commands()
    help_commands = '\n'.join([': '.join(i) for i in commands.items()])
    args = create_args_parser(help_commands).parse_args()
    initparams = vars(args)
    client = VerisureAPIClient(**initparams)
    output = client.operate_alarm(args.COMMAND)
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
