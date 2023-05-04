from flask import Flask, request as flask_req, Response
from os import environ
from helper import cfg, log_stuff, send_request

import processors


app = Flask(__name__)
app.config["DEBUG"] = False


@app.route('/', defaults={'path': ''})
@app.route('/<service>/<path:path>', methods=['GET', 'POST'])
def api(service, path):
    request = flask_req
    if service in cfg["services"]:

        required_processing = cfg["services"][service]["processors"]
        target = cfg["services"][service]["target"] + path

        log_stuff([request.remote_addr, ";".join(request.args)])

        for proc_name in required_processing:
            processor = getattr(processors, proc_name)
            request = processor(request)

    return send_request(request, target)


if __name__ == "__main__":
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
