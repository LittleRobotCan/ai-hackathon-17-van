# -*- coding: utf-8 -*-
import requests
import time
import cv2
import operator
import numpy as np
from PIL import Image

from emotions_api import _key

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


def render_result(result, img):

    for face in result:
        face_rectangle = face['faceRectangle']
        cv2.rectangle(img, (face_rectangle['left'], face_rectangle['top']),
                      (face_rectangle['left'] + face_rectangle['width'],
                       face_rectangle['top'] + face_rectangle['height']),
                      color=(255, 0, 0), thickness=5)

        curr_emotion = max(face['scores'].items(), key=operator.itemgetter(1))[0]

        emo = "%s" % curr_emotion
        cv2.putText(img, emo, (face_rectangle['left'], face_rectangle['top']-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 0, 0), 2)

if __name__ == "__main__":
    url_image = 'http://static.politico.com/dims4/default/bf5a744/2147483647/resize/1160x%3E/quality/90/?url=http%3A%2F%2Fstatic.politico.com%2Fff%2Feb%2F09e4a2184bf89e83cba50dcfab01%2Ftrump-angry-finger-speech.jpg'
    json = {'URL': url_image}

    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': _key,
        'Content-Type': 'application/json'
    }

    data = None
    params = None

    result = process_request(json, data, headers, params)

    if result is not None:
        # Load the original image, fetched from the URL
        arr = np.asarray(bytearray(requests.get(url_image).content), dtype=np.uint8)
        img = cv2.cvtColor(cv2.imdecode(arr, -1), cv2.COLOR_BGR2RGB)

        render_result(result, img)

        img_toshow = Image.fromarray(img, 'RGB')
        img_toshow.show()