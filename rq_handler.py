import processors
from helper import log_stuff
from requests import request as rr
from flask import Response


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


def process_request(args):
    flask_req, required_processing, target = args
    params = params_from_req(flask_req).to_dict()
    data = flask_req.get_data()
    log_stuff([flask_req.remote_addr, ";".join(params)])

    for proc_name in required_processing:
        processor = getattr(processors, proc_name)
        params, data = processor(params, data)

    return send_request(flask_req, target, params, data)


def send_request(request, target, params=None, data=None):
    if not params:
        params = params_from_req(request)
    if not data:
        data = request.get_data()

    res = rr(
        method=request.method,
        url=target,
        headers={k: v for k, v in request.headers},
        data=data,
        params=params,
        cookies=request.cookies,
        allow_redirects=False,
    )

    headers = [
        (k, v) for k, v in res.raw.headers.items()
    ]

    response = Response(res.content, res.status_code, headers)
    return response
