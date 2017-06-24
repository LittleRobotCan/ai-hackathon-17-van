# -*- coding: utf-8 -*-
import httplib
import urllib
import requests
import json
import time
import cv2
import operator

from msft_emotion_api import _colors

_url = 'https://westus.api.cognitive.microsoft.com/emotion/v1.0/recognizeinvideo'
_maxNumRetries = 10


def emotion_post_video(json, data, headers, param_option):

    params = urllib.urlencode({
        # Request parameters
        'outputStyle': param_option
    })

    retries = 0

    while True:
        if json is not None and data is not None:
            raise Exception("Too many inputs!")
        else:
            response = requests.request('POST', _url, json=json, data=data, headers=headers, params=params)

        if response.status_code == 429:
            print "Message: %s" % response.json()['error']['message']

            if retries <= _maxNumRetries:
                time.sleep(5)
                retries += 1
                continue
            else:
                raise Exception("Failed after multiple retries!")

        elif response.status_code == 202:
            location = response.headers["Operation-Location"]

        else:
            raise Exception("Error {0}: {1}".format(response.status_code, response.content))

        break

    return location.split("/")[-1]


def get_emotion_results(operation_id, key):

    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': key
    }

    conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
    conn.request("GET", "/emotion/v1.0/operations/" + operation_id, headers=headers)
    response = conn.getresponse()
    data = response.read()
    data = json.loads(data)
    conn.close()

    if data["status"] == "Running":
        print data
        raise Exception("Still Processing")

    elif data["status"] == "Succeeded":
        return data

    else:
        raise Exception("Processing Failed")


def render_emotion_result_video(result, img, width, height):

    for face_rectangle in result:
        color = _colors[(face_rectangle['id'] + 1) % len(_colors)]

        cv2.rectangle(img, (int(round(face_rectangle['x']*width, 0)), int(round(face_rectangle['y']*height, 0))),
                      (int(round((face_rectangle['x'] + face_rectangle['width'])*width, 0)),
                       int(round((face_rectangle['y'] + face_rectangle['height'])*height, 0))),
                      color=color, thickness=2)

        curr_emotion, curr_emotion_score = max(face_rectangle['scores'].items(), key=operator.itemgetter(1))
        emo = "Face" + str(face_rectangle['id']) + ":" + str(curr_emotion) + str(round(curr_emotion_score, 1))

        cv2.putText(img, emo, (int(round(face_rectangle['x']*width, 0)), int(round(face_rectangle['y']*height, 0))-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)