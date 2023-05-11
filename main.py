from flask import Flask, request as flask_req
from os import environ
from helper import cfg, processors4path, log_stuff
from rq_handler import process_args_and_send, send_request, req2args
from rq import Connection, Worker, Queue
import redis

app = Flask(__name__)
app.config["DEBUG"] = False

try:
    def redis_conn():
        redis_settings = cfg["redis"]
        if redis_settings["on"] < 1:
            return None
        else:
            redis_url = redis_settings["url"] + ":" + redis_settings["port"]
            conn = redis.from_url(redis_url)
            return conn


    def redis_queue():
        redis_settings = cfg["redis"]
        if redis_settings["on"] < 1:
            return None
        else:
            conn = redis_conn()
            q = Queue(connection=conn)
            return q


    q = redis_queue()
    conn = redis_conn()

    with Connection(conn):
        worker = Worker(list(map(Queue, ['default'])))
        worker.work()

except ImportError:
    q = None


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

