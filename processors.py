from os import path as px
from requests import get
from re import search
from json import loads, dumps


def add_solr_highlight(params, data):
    params["hl.fl"] = "media_txt"
    params["hl"] = "true",
    params["useFastVectorHighlighter"] = "true"
    params["hl.highlightMultiTerm"] = "true"
    params["hl.fragmentsBuilder"] = "colored"
    params["hl.fragsize"] = 220
    params["hl.snippets"] = 3
    return params, data


def sort_default(params, data):
    if params["q"] == "*:*":
        params["sort"] = "id desc"
    return params, data


def index_media(params, data, process_params):

    ip = process_params["ip"]
    files_dir = process_params["files_dir"]
    repo = process_params["repo"]
    date_field = process_params["date_field"]
    texase_addr = process_params["texase_addr"]
    omeka_api_addr = process_params["omeka_api_addr"]
    key_identity = process_params["key_identity"]
    key_credential = process_params["key_credential"]

    if key_credential and key_identity:
        api_key = "&key_identity=" + key_identity + "&key_credential=" + key_credential
    else:
        api_key = ""

    def txt_from_file(filepath):
        return get("{}extract?file={}".format(texase_addr, filepath)).text

    def renew_file(filepath, idx, repo):
        get("{}renew?file={}&id={}&repo={}".format(texase_addr, filepath, idx, repo))

    def get_filepaths(idx):
        try:
            media_json = get(omeka_api_addr + "media?item_id=" + idx + api_key).json()
            media_public_json = get(omeka_api_addr + "media?item_id=" + idx).json()
            
            media = sorted([x["o:original_url"] for x in media_json])
            media_public = sorted([x["o:original_url"] for x in media_public_json])
            
            return media, int(media==media_public)
        except:
            return [], 0

    adds = data.replace(",\"add\":", "}\n{\"add\":").split("\n")
    print(len(adds))
    newadds = []
    for add in adds:
        data_json = loads(add)

        if "add" not in data_json.keys():
            return params, data

        if "doc" not in data_json["add"].keys():
            return params, data

        doc = data_json["add"]["doc"]

        try:
            item_id = doc["id"].split("items/")[1]
        except:
            item_id = -1
        filepaths, doc["private_media"] = get_filepaths(item_id)
        filepaths = [x.replace(ip, files_dir) for x in filepaths]
        doc["media_txt"] = []
        hasMedia = []

        if date_field in doc:
            try:
                year = search(r"[12][0-9]{3}", doc[date_field]).group()
                doc["year_i"] = year
            except:
                pass

        for filepath in filepaths:
            path, ext = px.splitext(filepath)
            hasMedia.append(ext[1:])
            renew_file(filepath, item_id, repo)
            doc["media_txt"].append(txt_from_file(filepath))

        doc["hasMedia"] = list(set(hasMedia))

        data_json["add"]["doc"] = doc
        newadds.append(dumps(data_json))

    data = "\n".join(newadds).replace("}\n{\"add\":", ",\"add\":")

    return params, data
