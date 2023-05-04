from json import load
from os import path as px
from requests import request as rr
from flask import Response


def load_conf(path=None):
    if not path:
        path = px.join(px.dirname(__file__), "config.json")
    with open(path, "r", encoding="utf-8") as cf:
        return load(cf)


cfg = load_conf()


def log_stuff(stuff):
    if "log" in cfg and cfg["log"]:
        try:
            with open(cfg["log"], "a+", encoding="utf-8") as lf:
                lf.write("\t".join([str(x) for x in stuff]) + "\n")
        except:
            pass


def send_request(request, target):
    res = rr(
        method=request.method,
        url=target,
        headers={k: v for k, v in request.headers if k.lower() == 'host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )

    # region exlcude some keys in :res response
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [
        (k, v) for k, v in res.raw.headers.items()
        if k.lower() not in excluded_headers
    ]

    response = Response(res.content, res.status_code, headers)
    return response