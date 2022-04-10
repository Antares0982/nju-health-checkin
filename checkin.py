#!/usr/bin/env python3
"""
File: checkin.py
Project: nju-health-checkin
Author: Maxwell Lyu https://github.com/Maxwell-Lyu
-----
Last Modified: Tuesday, 28th December 2021 3:53:25 pm
Modified By: Antares (antares0982@gmail.com)
-----
Copyright (C) 2021 Maxwell Lyu
"""

import base64
import json
import os
import random
from configparser import ConfigParser

import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto.Util import Padding


def encryptAES(_p0: str, _p1: str) -> str:
    _chars = list("ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678")

    def _rds(len: int) -> str:
        return "".join(random.choices(_chars, k=len))

    def _gas(data: str, key0: str, iv0: str) -> bytes:
        encrypt = AES.new(
            key0.strip().encode("utf-8"), AES.MODE_CBC, iv0.encode("utf-8")
        )
        return base64.b64encode(encrypt.encrypt(Padding.pad(data.encode("utf-8"), 16)))

    return _gas(_rds(64) + _p0, _p1, _rds(16)).decode("utf-8")


def to_shell_urltext(s: str) -> str:
    s = "%20".join(s.split())
    s = s.replace("{", r"\{")
    s = s.replace("}", r"\}")
    return s


def main():
    # get config
    cfgfile = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "config.ini"
    )
    cfgparser = ConfigParser()
    cfgparser.read(cfgfile)

    username = cfgparser["check"]["ID"]
    password = cfgparser["check"]["PASSWD"]

    try:
        location = cfgparser["check"]["location"]
    except KeyError:
        location = None
    if location == "":
        location = None
    try:
        proxy = cfgparser["check"]["proxy"]
    except KeyError:
        proxy = None
    if proxy == "":
        proxy = None

    if "http_proxy" in os.environ:
        os.environ.pop("http_proxy")
    if "https_proxy" in os.environ:
        os.environ.pop("https_proxy")

    # login
    url_login = r"https://authserver.nju.edu.cn/authserver/login"
    url_list = r"http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/getApplyInfoList.do"
    session = requests.Session()
    session.trust_env = False  # do not use proxy setting in env

    if proxy is not None:
        response = session.get(url_login, proxies={
                               "http": proxy, "https": proxy
                               })
    else:
        response = session.get(url_login, proxies={})

    soup = BeautifulSoup(response.text, "html.parser")
    soup.select_one("#pwdDefaultEncryptSalt").attrs["value"]
    data_login = {
        "username": username,
        "password": encryptAES(
            password, soup.select_one("#pwdDefaultEncryptSalt").attrs["value"]
        ),
        "lt": soup.select_one('[name="lt"]').attrs["value"],
        "dllt": "userNamePasswordLogin",
        "execution": soup.select_one('[name="execution"]').attrs["value"],
        "_eventId": soup.select_one('[name="_eventId"]').attrs["value"],
        "rmShown": soup.select_one('[name="rmShown"]').attrs["value"],
    }
    session.post(url_login, data_login)

    # get info
    raw = session.get(url_list)
    content = raw.json()

    # apply
    data = next(x for x in content["data"] if x.get("TJSJ") != "")

    data["WID"] = content["data"][0]["WID"]
    fields = [
        "WID",
        "CURR_LOCATION",
        "IS_TWZC",  # 体温正常
        "IS_HAS_JKQK",  # 健康情况
        "JRSKMYS",  # 今日苏康码颜色
        "JZRJRSKMYS",  # 居住人今日苏康码颜色
        "SFZJLN",  # 是否最近离宁
        "ZJHSJCSJ"  # 最近核酸检测时间
    ]

    if location is not None:
        data["CURR_LOCATION"] = location

    result = session.get(
        "http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/saveApplyInfos.do?"
        + "&".join([key + "=" + data[key] for key in fields])
    )

    answer = json.loads(result.text)
    answer["location"] = data["CURR_LOCATION"]

    answer = str(answer)

    if result.status_code != 200:
        answer = f"Checkin failed with status code {result.status_code}"

    if "TO_HTML" in os.environ:
        answer = to_shell_urltext(answer)

    print(answer)


if __name__ == "__main__":
    main()
