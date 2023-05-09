from flask import Flask, request as flask_req
from os import environ
from helper import cfg, log_stuff, send_request, params_from_req

import processors


app = Flask(__name__)
app.config["DEBUG"] = False


@app.route('/', defaults={'path': ''})
@app.route('/<service>/<path:path>', methods=['GET', 'POST'])
def api(service, path):
    params = params_from_req(flask_req)
    log_stuff([flask_req.remote_addr, ";".join(params)])

    if service in cfg["services"]:

        required_processing = cfg["services"][service]["processors"]
        target = cfg["services"][service]["target"] + path

        for proc_name in required_processing:
            processor = getattr(processors, proc_name)
            params = processor(params)

        return send_request(flask_req, params, target)


if __name__ == "__main__":
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
