# -*- coding: utf-8 -*-
import httplib
import urllib
import json

from emotions_api import _key


def post_video(video, key, param_option):
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': key
    }

    params = urllib.urlencode({
        # Request parameters
        'outputStyle': param_option
    })

    conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
    conn.request("POST", "/emotion/v1.0/recognizeinvideo?%s" % params, json.dumps(video), headers)
    response = conn.getresponse()
    location = response.getheader('operation-location')
    conn.close()

    return location.split("/")[-1]


def get_results(operation_id, key):

    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': key
    }

    conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
    conn.request("GET", "/emotion/v1.0/operations/" + operation_id, headers=headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()

    return data


if __name__ == "__main__":
    param = "perFrame"  # or "aggregate"

    video_filename = {"URL": "https://fsarquivoeastus.blob.core.windows.net/public0/WhatsApp-Video-20160727.mp4"}

    oid = post_video(video_filename, _key, param)
    print oid

    import time
    # wait for 20 seconds to read the output
    # this might need to be longer
    time.sleep(20)

    print get_results(oid, _key)