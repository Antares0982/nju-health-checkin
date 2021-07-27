# NJU Health Checkin Script
# Copyright (C) 2021 Maxwell Lyu https://github.com/Maxwell-Lyu

import os
import json
import random
import base64
import requests
from Crypto.Cipher import AES
from Crypto.Util import Padding
from bs4 import BeautifulSoup


class JsonDict(dict):
    """general json object that allows attributes to be bound to and also behaves like a dict"""

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, attr, value):
        self[attr] = value


def main():
    def encryptAES(_p0: str, _p1: str) -> str:
        _chars = list('ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678')

        def _rds(len: int) -> str:
            return ''.join(random.choices(_chars, k=len))

        def _gas(data: str, key0: str, iv0: str) -> bytes:
            encrypt = AES.new(key0.strip().encode('utf-8'),
                              AES.MODE_CBC, iv0.encode('utf-8'))
            return base64.b64encode(encrypt.encrypt(Padding.pad(data.encode('utf-8'), 16)))
        return _gas(_rds(64) + _p0, _p1, _rds(16)).decode('utf-8')

    username = os.environ['NJU_USER']
    password = os.environ['NJU_PASS']
    url_login = r'https://authserver.nju.edu.cn/authserver/login'
    url_list = r'http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/getApplyInfoList.do'
    url_apply = r'http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/saveApplyInfos.do'
    session = requests.Session()

    # login
    response = session.get(url_login)
    soup = BeautifulSoup(response.text, 'html.parser')
    soup.select_one("#pwdDefaultEncryptSalt").attrs['value']
    data_login = {
        'username': username,
        'password': encryptAES(password, soup.select_one("#pwdDefaultEncryptSalt").attrs['value']),
        'lt': soup.select_one('[name="lt"]').attrs['value'],
        'dllt': "userNamePasswordLogin",
        'execution': soup.select_one('[name="execution"]').attrs['value'],
        '_eventId': soup.select_one('[name="_eventId"]').attrs['value'],
        'rmShown': soup.select_one('[name="rmShown"]').attrs['value'],
    }
    session.post(url_login, data_login)

    # list
    content = session.get(url_list).json()

    # apply
    data = next(x for x in content['data'] if x.get('TJSJ') != '')
    data['WID'] = content['data'][0]['WID']
    fields = [
        'WID',
        'CURR_LOCATION',
        'IS_TWZC',
        'IS_HAS_JKQK',
        'JRSKMYS',
        'JZRJRSKMYS'
    ]
    result = session.get('http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/saveApplyInfos.do?' +
                         '&'.join([key + '=' + data[key] for key in fields]))

    answer = json.loads(result.text, object_hook=JsonDict)
    answer.data.location = data['CURR_LOCATION']
    print(answer)

    if result.status_code != 200:
        exit(1)


main()
