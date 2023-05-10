from flask import Flask, request as flask_req
from os import environ
from helper import cfg, processors4path
from rq_handler import process_request, send_request


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

    required_processing, for_redis = processors4path(service, path)
    if len(required_processing) == 0:
        return send_request(flask_req, target)

    else:
        args = flask_req, required_processing, target

        if q and for_redis:
            job = q.enqueue(process_request, args)
            return "sent to redis que, id:" + str(job.get_id())
        else:
            return process_request(args)


if __name__ == "__main__":
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

