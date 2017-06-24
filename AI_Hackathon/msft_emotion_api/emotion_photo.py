# -*- coding: utf-8 -*-
import requests
import time
import cv2
import operator
import numpy as np
from PIL import Image

from msft_emotion_api import _colors

_url = 'https://westus.api.cognitive.microsoft.com/emotion/v1.0/recognize'
_maxNumRetries = 10


def process_request(json, data, headers, params=None):
    retries = 0
    result = None

    while True:
        if json is not None and data is not None:
            raise Exception("Too many inputs!")
        else:
            response = requests.request('POST', _url, json=json, data=data, headers=headers, params=params)

        if response.status_code == 429:
            print "Message: %s" % response.json()['error']['message']

            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                raise Exception("Failed after multiple retries!")

        elif response.status_code == 200 or response.status_code == 201:
            if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                result = None
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                if 'application/json' in response.headers['content-type'].lower():
                    result = response.json() if response.content else None
                elif 'image' in response.headers['content-type'].lower():
                    result = response.content
        else:
            raise Exception("Error {0}: {1}".format(response.status_code, response.json()['error']['message']))

        break

    return result


def render_emotion_result_photo(result, img):

    for face in result:
        face_rectangle = face['faceRectangle']

        color = _colors[len(_colors) % (face_rectangle['id'] + 1)]

        cv2.rectangle(img, (face_rectangle['left'], face_rectangle['top']),
                      (face_rectangle['left'] + face_rectangle['width'],
                       face_rectangle['top'] + face_rectangle['height']),
                      color=color, thickness=5)

        curr_emotion = max(face['scores'].items(), key=operator.itemgetter(1))[0]

        emo = "%s" % curr_emotion
        cv2.putText(img, emo, (face_rectangle['left'], face_rectangle['top']-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    color, 1)