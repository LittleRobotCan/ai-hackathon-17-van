# -*- coding: utf-8 -*-
import httplib
import urllib
import requests
import json
import time
import cv2
import operator

from msft_emotion_api import _face_tracking_key, _colors

_url = 'https://westus.api.cognitive.microsoft.com/video/v1.0/trackface'
_maxNumRetries = 10


def post_face_tracking_video(json, data, headers):

    params = urllib.urlencode({})

    retries = 0

    while True:
        if json is not None and data is not None:
            raise Exception("Too many inputs!")
        else:
            response = requests.request('POST', _url, json=json, data=data, headers=headers, params=params)

        if response.status_code == 429:
            print "Message: %s" % response.json()['error']['message']

            if retries <= _maxNumRetries:
                time.sleep(10)
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


def get_face_tracking_results(operation_id, key):

    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': key
    }

    conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
    conn.request("GET", "/video/v1.0/operations/" + operation_id, headers=headers)
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

def render_ft_result_video(result, img, width, height):

    for face_rectangle in result:
        #color = _colors[len(_colors) % (face_rectangle['id'] + 1)]

        cv2.rectangle(img, (int(round(face_rectangle['x']*width, 0)), int(round(face_rectangle['y']*height, 0))),
                      (int(round((face_rectangle['x'] + face_rectangle['width'])*width, 0)),
                       int(round((face_rectangle['y'] + face_rectangle['height'])*height, 0))),
                      color=(255,255,255), thickness=2)

        cv2.putText(img, "Face: " + str(face_rectangle['id']), (int(round(face_rectangle['x']*width, 0)), int(round(face_rectangle['y']*height, 0))-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)