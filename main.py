from flask import Flask, request as flask_req
from os import environ
from helper import cfg, processors4path, log_stuff
from request_handler import process_args_and_send, send_request, req2args
try:
    from redisworks import q
except ImportError:
    q = None


app = Flask(__name__)
app.config["DEBUG"] = False


@app.route('/', defaults={'path': ''})
@app.route('/<service>/<path:path>', methods=['GET', 'POST'])
def api(service, path):

    if service not in cfg["services"]:
        return None

    target = cfg["services"][service]["target"] + path
    args = req2args(flask_req, target)
    required_processing, for_redis = processors4path(service, path)

    if len(required_processing) == 0:
        return send_request(args)

    args += (required_processing,)
    log_stuff([flask_req.remote_addr, ";".join([str(x) for x in args])])

    if q and for_redis:
        job = q.enqueue(process_args_and_send, args)
        return "sent to redis que, id:" + str(job.get_id())

    return process_args_and_send(args)


if __name__ == "__main__":
    port = int(environ.get("PORT", 5002))
    app.run(host='0.0.0.0', port=port)

