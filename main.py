from flask import Flask, request, render_template
from os import environ
from helper import cfg
from rq_handler import process_req
from redisworks import redis_q as q


app = Flask(__name__)
app.config["DEBUG"] = False


@app.route('/<service>', methods=['POST', 'GET'])
def api(service):
    if service in cfg["services"]:
        function, args = process_req(request)
        if q:
            job = q.enqueue(function, args)
            return "sent to redis que, id:" + str(job.get_id())
        else:
            return function(args)


if __name__ == "__main__":
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
