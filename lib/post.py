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
    url = params['url']

    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"title\"\r\n\r\n" \
        +item["title"]+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data;"\
        " name=\"status\"\r\n\r\npublish\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data;"\
        " name=\"content\"\r\n\r\n"+item["description"]+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data;"\
        " name=\"tags\"\r\n\r\n"+item["tags"]+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition:"\
        " form-data; name=\"categories\"\r\n\r\n1377\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition:"\
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

        print(payload)
        print("--- "+tag+" ---")
        print(response.text)
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




