import json
import sys
import requests
from requests.exceptions import (
    SSLError,
    ConnectionError,
    ConnectTimeout)
from unidecode import unidecode
import time

def wordpress_create_post(item, params):
    url = params['url']+"posts"
    print("Posting "+item["title"])
    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"title\"\r\n\r\n" \
        +item["title"]+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data;"\
        " name=\"status\"\r\n\r\npublish\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data;"\
        " name=\"content\"\r\n\r\n"+item["description"]+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data;"\
        " name=\"tags\"\r\n\r\n"+item["tags"]+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition:"\
        " form-data; name=\"categories\"\r\n\r\n"+item["category"]+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition:"\
        " form-data; name=\"slug\"\r\n\r\n"+unidecode(item["slug"]).replace(" ", "-")+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'authorization': "Basic "+params['token'],
        'cache-control': "no-cache"
        }
    
    while True:
        try:
            response = requests.request("POST", url, data=payload.encode("utf-8"), headers=headers)
            break
        except (SSLError, ConnectionError, ConnectTimeout):
            print("Connection error. Retry in 2s")
            time.sleep(2)

    print(response)

    jsonify_response = json.loads(response.text)
    if "id" in jsonify_response:
        return True
    return False


def get_wordpress_tags(url):
    url = url+"tags"
    tags_dic = dict()
    tags_list = list()
    response = requests.request("GET", url)
    print(response.text)
    jsonify_response = json.loads(response.text)
    if jsonify_response:
        for elt in jsonify_response:
            tags_dic[elt['name']] = elt['id']
            tags_list.append(elt['name'])
    return tags_dic, tags_list


def create_tag(tag, url, auth_key):
    url = url+"tags"
    try:
        payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\n"+tag+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
        headers = {
            'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            'authorization': "Basic "+auth_key
            }
        while True:
            try:
                response = requests.request(
                    "POST",
                    url,
                    data=payload,
                    headers=headers
                )
                break
            except (SSLError, ConnectionError, ConnectTimeout):
                print("Connection error. Retry in 2s")
                time.sleep(2)

        jsonify_response = json.loads(response.text)
        if jsonify_response:
            if "id" in jsonify_response:
                print(jsonify_response)
                return jsonify_response["id"]
            if "data" in jsonify_response and jsonify_response["code"] != "empty_term_name":
                print(jsonify_response)
                return jsonify_response["data"]["term_id"]

        return None
    except json.decoder.JSONDecodeError:
        return None


def get_category_id(url, auth_key, cat_name):
    url = url+"categories?page=1&per_page=100"
    payload = ""
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'authorization': "Basic "+auth_key,
        'cache-control': "no-cache",
        'postman-token': "fed0df13-04d9-e212-b64d-717c89e1f99a"
    }

    response = requests.request("GET", url, data=payload, headers=headers)

    jsonify_response = json.loads(response.text)

    for j_res in jsonify_response:
        if unidecode(j_res["name"]).lower() == cat_name:
            return j_res["id"]
    return 1377
