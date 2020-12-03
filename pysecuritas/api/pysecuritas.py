# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""

import argparse
import base64
import itertools
import time
from datetime import datetime

from pysecuritas.core.commands import DALARM_OPS, DAPI_OPS, ALARM_OPS, API_OPS
from pysecuritas.core.session import Session


class pysecuritas():
    PANEL = 'SDVFAST'
    CALLBY = 'AND_61'
    TIMEFILTER = '3'
    RATELIMIT = 1

    def __init__(self, args: argparse.Namespace):
        self.user = args.username
        self.sensor = args.sensor
        self.LOGIN_PAYLOAD = {'Country': args.country,
                              'user': self.user, 'pwd': args.password, 'lang': args.language}
        self.OP_PAYLOAD = {'Country': args.country, 'user': self.user,
                           'pwd': args.password, 'lang': args.language, 'panel': self.PANEL,
                           'callby': self.CALLBY, 'numinst': args.installation}
        self.OUT_PAYLOAD = {'Country': args.country, 'user': self.user,
                            'pwd': args.password, 'lang': args.language, 'numinst': '(null)'}
        self.session = Session().set_username(args.username).set_password(args.password).set_country(
            args.country).set_lang(args.language).set_installation(args.installation)

    def return_commands(self):
        all_ops = dict(itertools.chain(
            DALARM_OPS.items(), DAPI_OPS.items()))
        return all_ops

    def call_verisure_get(self, method, parameters):
        time.sleep(self.RATELIMIT)
        if method == 'GET':
            return self.session.get(parameters)

        if method == 'POST':
            return self.session.post(parameters)

    def op_verisure(self, action, hash, id):
        payload = self.OP_PAYLOAD
        payload.update({'request': action, 'hash': hash, 'ID': id})
        if action == 'IMG':
            payload.update(
                {'device': self.sensor, 'instibs': self.instibs, 'idservice': '1'})
        if action == 'INF':
            payload.update({'idsignal': self.idsignal,
                            'signaltype': self.signaltype})
        if action in ALARM_OPS:
            payload['request'] = action + '1'
            self.call_verisure_get('GET', payload)
            payload['request'] = action + '2'
            output = self.call_verisure_get('GET', payload)
            res = output['PET']['RES']
            while res != 'OK':
                output = self.call_verisure_get('GET', payload)
                res = output['PET']['RES']
        elif (action in API_OPS) or (action == 'INF'):
            if action == 'ACT_V2':
                payload.update(
                    {'timefilter': self.TIMEFILTER, 'activityfilter': '0'})
            output = self.call_verisure_get('GET', payload)
        clean_output = output['PET']
        del clean_output['BLOQ']
        return clean_output

    def generate_id(self):
        ID = 'AND_________________________' + self.user + \
             datetime.now().strftime('%Y%m%d%H%M%S')
        return ID

    def get_login_hash(self):
        self.session.connect()

        return self.session.login_hash

    def logout(self, hash):
        self.session.close()

    def operate_alarm(self, action):
        if (action in ALARM_OPS) or (action in API_OPS):
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
