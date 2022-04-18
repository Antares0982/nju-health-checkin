#!/usr/bin/env python3
'''
File: checkin.py
Project: nju-health-checkin
Created Date: Sunday, April 17th 2022, 4:12:13 pm
Author: antares0982@gmail.com
Copyright (c) 2022 Antares
'''


import json
import os
from configparser import ConfigParser
from typing import Dict, List, Optional, Tuple

import requests

FIELDS = [
    "WID",
    "CURR_LOCATION",
    "IS_TWZC",  # 体温正常
    "IS_HAS_JKQK",  # 健康情况
    "JRSKMYS",  # 今日苏康码颜色
    "JZRJRSKMYS",  # 居住人今日苏康码颜色
    "SFZJLN",  # 是否最近离宁
    "ZJHSJCSJ"  # 最近核酸检测时间
]


def to_shell_urltext(s: str) -> str:
    s = "%20".join(s.split())
    s = s.replace("{", r"\{")
    s = s.replace("}", r"\}")
    return s


def getTempAuth(session: requests.Session, cookie: str) -> str:
    session.get(
        "https://authserver.nju.edu.cn/authserver/login?service=http://ehallapp.nju.edu.cn/psfw/sys/tzggapp/mobile/getUnReadCount.do",
        headers={
            "cookie": cookie,
        })
    ans: List[str] = []
    ans.append("iPlanetDirectoryPro=" +
               session.cookies.get("iPlanetDirectoryPro"))
    ans.append("route="+session.cookies.get("route"))
    ans.append("MOD_AUTH_CAS="+session.cookies.get("MOD_AUTH_CAS"))
    ans.append("_WEU="+session.cookies.get("_WEU"))

    return "; ".join(ans)


def grepLastCheckinInfo(cookie: str, location: Optional[str] = None) -> Dict[str, str]:
    session = requests.Session()
    url_list = r"http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/getApplyInfoList.do"
    # grep info directly, use cookie
    raw = session.get(f"https://authserver.nju.edu.cn/authserver/login?service={url_list}", headers={
        "cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; ONEPLUS A6010 Build/QKQ1.190716.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/100.0.4896.88 Mobile Safari/537.36  cpdaily/8.2.7 wisedu/8.2.7",
    })

    content = raw.json()

    # apply
    data = next(x for x in content["data"] if x.get("TJSJ") != "")

    data["WID"] = content["data"][0]["WID"]
    if location is not None:
        data["CURR_LOCATION"] = location

    return data


def getConfig() -> Tuple[str, Optional[str], Optional[str]]:
    cfgfile = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "config.ini"
    )
    cfgparser = ConfigParser()
    cfgparser.read(cfgfile)

    cookie = os.getenv("NJU_COOKIE")
    if cookie is None:
        cookie = cfgparser["check"]["cookie"]

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

    return cookie, location, proxy


def main():
    # get config
    cookie, location, proxy = getConfig()

    # create session
    session = requests.Session()
    # default not use proxy if the field "proxy" in `config.ini` is not set, even if there is a system proxy.
    # github action blocks connection which has `trust_env = False`.
    if "NJU_COOKIE" not in os.environ:
        session.trust_env = False
    if proxy is not None:
        # set manually specified proxy
        session.proxies = {"http": proxy, "https": proxy}

    # get the data in last checkin
    data = grepLastCheckinInfo(cookie, location)

    # get temporary auth cookie MOD_AUTH_CAS
    cookie += "; "+getTempAuth(session, cookie)

    # apply
    result = session.get(
        "http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/saveApplyInfos.do?" +
        "&".join([key + "=" + data[key] for key in FIELDS]),
        headers={
            "cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; ONEPLUS A6010 Build/QKQ1.190716.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/100.0.4896.88 Mobile Safari/537.36  cpdaily/8.2.7 wisedu/8.2.7",
        })

    answer = json.loads(result.text)
    answer["location"] = data["CURR_LOCATION"]

    answer = str(answer)

    if result.status_code != 200:
        answer = f"Checkin failed with status code {result.status_code}"

    if "TO_HTML" in os.environ:
        answer = to_shell_urltext(answer)

    # print to stdout. will be sent to telegram bot in `run.sh`
    print(answer)


if __name__ == "__main__":
    main()
