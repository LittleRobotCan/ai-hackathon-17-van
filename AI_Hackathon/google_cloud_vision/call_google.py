import requests
import time
import json
import base64
from google_cloud_vision import _key

_url = 'https://vision.googleapis.com/v1/images:annotate'
_maxNumRetries = 10

def process_request(data, key=_key):
    retries = 0
    result = None

    headers = {
        # Request headers
        'Content-Type': 'application/json'
        }

    body = {"requests": [
                {"image": {
                    "content": base64.b64encode(data).decode('UTF-8')
                  },
                  "features": [
                    {"type": "FACE_DETECTION"}
                  ]
                }
              ]
            }

    while True:
        response = requests.request('POST', _url + '?key=' + _key, data=json.dumps(body), headers=headers)

        if response.status_code == 429:
            print "Message: %s" % response.json()['error']['message']

            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                raise Exception("Failed after multiple retries!")

        elif response.status_code == 200 or response.status_code == 201:
           result = response.content
        else:
            raise Exception("Error {0}: {1}".format(response.status_code, response.json()['error']['message']))

        break

    return result

# The name of the image file to annotate
file_name = r'C:\Users\tony.guo\Desktop\download.jpg'

import io

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

print process_request(content)
