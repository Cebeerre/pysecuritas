#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import xmltodict
from datetime import datetime
import time
import json

class VerisureAPIClient():
    BASE_URL='https://mob2217.securitasdirect.es:12010/WebService/ws.do'

    def __init__(self, user,pwd,numinst,panel,country,lang,rate):
        self.user = user
        self.rate = rate
        self.LOGIN_PAYLOAD = { 'Country': country, 'user':user, 'pwd': pwd, 'lang': lang }
        self.OP_PAYLOAD = { 'Country': country, 'user':user, 'pwd': pwd, 'lang': lang, 'panel': panel, 'numinst': numinst}
        self.OUT_PAYLOAD = { 'Country': country, 'user':user, 'pwd': pwd, 'lang': lang, 'numinst': '(null)'}

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

    def op_verisure(self, action,hash,id):
        payload = self.OP_PAYLOAD
        payload.update({'request': action+'1', 'hash': hash, 'ID': id})
        self.call_verisure_get('GET',payload)
        payload['request'] = action+'2'
        output = self.call_verisure_get('GET',payload)
        res = output['PET']['RES']
        while res != 'OK':
            output = self.call_verisure_get('GET',payload)
            res = output['PET']['RES']
        return json.dumps(output)

    def generate_id(self):
        ID='IPH_________________________'+self.user+datetime.now().strftime("%Y%m%d%H%M%S")
        return ID

    def get_login_hash(self):
        payload = self.LOGIN_PAYLOAD
        payload.update({'request': 'LOGIN', 'ID': self.generate_id()})
        output = self.call_verisure_get('POST',payload)
        return output['PET']['HASH']

    def logout(self,hash):
        payload = self.OUT_PAYLOAD
        payload.update({'request': 'CLS', 'hash': hash, 'ID': self.generate_id()})
        output = self.call_verisure_get('GET', payload)
        return json.dumps(output)

    def get_panel_status(self):
        hash = self.get_login_hash()
        id = self.generate_id()
        status = self.op_verisure('EST', hash, id)
        self.logout(hash)
        return status

    def arm_outside(self):
        hash = self.get_login_hash()
        id = self.generate_id()
        status = self.op_verisure('PERI', hash, id)
        self.logout(hash)
        return status

    def arm_total_inside(self):
        hash = self.get_login_hash()
        id = self.generate_id()
        status = self.op_verisure('ARM', hash, id)
        self.logout(hash)
        return status

    def disarm_all(self):
        hash = self.get_login_hash()
        id = self.generate_id()
        status = self.op_verisure('DARM', hash, id)
        self.logout(hash)
        return status

    def arm_nigh(self):
        hash = self.get_login_hash()
        id = self.generate_id()
        status = self.op_verisure('ARMNIGHT', hash, id)
        self.logout(hash)
        return status

    def log(self):
        hash = self.get_login_hash()
        id = self.generate_id()
        payload = self.OP_PAYLOAD
        payload.update({'request': 'ACT_V2', 'hash':hash, 'ID':id, 'timefilter': '3', 'activityfilter': '0'})
        output = self.call_verisure_get('GET',payload)
        return json.dumps(output)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 8:
        print('Must provide Username Password Numinst Panel Country Lang Rate ACTION')
        sys.exit(1)
    client = VerisureAPIClient(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],int(sys.argv[7]))
    if sys.argv[8] == 'EST':
        output = client.get_panel_status()
    elif sys.argv[8] == 'PERI':
        output = client.arm_outside()
    elif sys.argv[8] == 'ARM':
        output = client.arm_total_inside()
    elif sys.argv[8] == 'ARMNIGHT':
        output = client.arm_nigh()
    elif sys.argv[8] == 'DARM':
        output = client.disarm_all()
    elif sys.argv[8] == 'ACT':
        output = client.log()

    print(output)
