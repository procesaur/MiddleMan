import processors
from requests import request as rr
from flask import Response
from copy import deepcopy


def params_from_req(req):
    query_parameters = req.args
    if len(query_parameters) == 0:
        query_parameters = req.form
    return query_parameters


def req2file(req):
    if "file" not in req.files:
        return None, None

    file_bytes = req.files["file"].read()
    filename = req.files["file"].filename

    if filename == "":
        return None, None

    return file_bytes, filename


def req2args(req, target):
    method = req.method
    headers = {k: v for k, v in req.headers}
    cookies = req.cookies

    params = params_from_req(req).to_dict()
    data = req.get_data()
    args = params, data, method, headers, cookies, target
    return args


def process_args_and_send(args):
    params, data, method, headers, cookies, target, required_processing = args

    params_o, data_o = deepcopy(params), deepcopy(data)

    for proc_name in required_processing:
        processor = getattr(processors, proc_name)
        params, data = processor(params, data)

    if not params:
        params = params_o
    if not data:
        data = data_o

    args = params, data, method, headers, cookies, target

    return send_request(args)


def send_request(args):
    params, data, method, headers, cookies, target = args

    if isinstance(data, str):
        data = data.encode('utf-8')

    res = rr(
        method=method,
        url=target,
        headers=headers,
        data=data,
        params=params,
        cookies=cookies,
        allow_redirects=False,
    )

    headers = [
        (k, v) for k, v in res.raw.headers.items()
    ]

    response = Response(res.content, res.status_code, headers)

    return response
