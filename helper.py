from json import load
from os import path as px


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


def processors4path(service, path):
    required_processing = []
    for_redis = False
    process_args = {}
    for pathx in cfg["services"][service]["paths"]:
        if pathx in path:
            required_processing += cfg["services"][service]["paths"][pathx]["processors"]
            if "redis" in cfg["services"][service]["paths"][pathx]:
                if cfg["services"][service]["paths"][pathx]["redis"] == 1:
                    for_redis = True
    if required_processing and cfg["services"][service]["process_args"]:
        for processor in required_processing:
            if cfg["services"][service]["process_args"][processor]:
                process_args[processor] = cfg["services"][service]["process_args"][processor]
    return required_processing, for_redis, process_args
