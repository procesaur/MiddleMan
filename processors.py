from os import path as px
from xmltodict import parse, unparse
from requests import get
from re import search


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


def index_media(params, data):

    ip = "http://127.0.0.1"
    files_dir = "/var/www/html"
    repo = "example_rgf"
    date_field = "dcterms_issued_txt"

    texase_addr = ip + ":5001/api/"
    omeka_api_addr = ip + "/api/"

    def txt_from_file(filepath):
        return get("{}extract?file={}".format(texase_addr, filepath)).text

    def renew_file(filepath, idx, repo):
        get("{}renew?file={}&id={}&repo={}".format(texase_addr, filepath, idx, repo))

    def get_id(src):
        id_str = [x["#text"] for x in src if x["@name"] == "id"][0]
        return id_str.split("items/")[1]

    def get_filepaths(idx):
        media = get(omeka_api_addr + "media?item_id=" + idx).json()
        return [x["o:original_url"] for x in media]

    def extract_year(doc):
        dateind = [i for i, x in enumerate(doc) if x["@name"] == date_field]
        if not dateind:
            return doc
        dateindex = dateind[0]
        year = search(r"[12][0-9]{3}", doc[dateindex]["#text"]).group()
        doc.append({'@name': 'year', '#text': year})
        return doc

    data_json = parse(data)

    if "update" not in data_json.keys():
        return params, data

    if "add" not in data_json["update"].keys():
        return params, data

    if "doc" not in data_json["update"]["add"].keys():
        return params, data

    if type(data_json["update"]["add"]["doc"]) is dict:
        docs = [data_json["update"]["add"]["doc"]]
    else:
        docs = data_json["update"]["add"]["doc"]

    newdocs = []
    for doc in docs:
        item_id = get_id(doc["field"])
        filepaths = get_filepaths(item_id)
        filepaths = [x.replace(ip, files_dir) for x in filepaths]
        media_txt = ""
        hasMedia = []

        doc["field"] = extract_year(doc["field"])

        for filepath in filepaths:
            path, ext = px.splitext(filepath)
            hasMedia.append(ext[1:])
            renew_file(filepath, item_id, repo)
            media_txt += "\n" + txt_from_file(filepath)

        hasMedia = list(set(hasMedia))
        for hm in hasMedia:
            doc["field"].append({'@name': 'hasMedia', '#text': hm})

        doc["field"].append({'@name': 'media_txt', '#text': media_txt})
        newdocs.append(doc)

    if docs:
        data_json["update"]["add"]["doc"] = newdocs

    data = unparse(data_json)
    return params, data
