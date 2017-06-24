from __future__ import division
import cv2
from msft_emotion_api import _emotion_key, _face_tracking_key
from msft_emotion_api.emotion_video import emotion_post_video, get_emotion_results, render_emotion_result_video
import json
import time


headers_em = {
        # Request headers
        'Ocp-Apim-Subscription-Key': _emotion_key,
        'Content-Type': 'application/octet-stream'
        }

headers_ft = {
        # Request headers
        'Ocp-Apim-Subscription-Key': _face_tracking_key,
        'Content-Type': 'application/octet-stream'
        }

video_path = r'videos\happy.mp4'

# data = open(video_path, 'rb').read()
# emotion_oid = emotion_post_video(None, data, headers_em, "perFrame")
# print emotion_oid
#
# time.sleep(20)

# emotion_oid = "99d15852-2241-4af0-aa8a-907e2f728fca" # Luke No
# emotion_oid = "206f31ac-64eb-40a7-b0ec-95f5a871691f" # Alfred FailedYou
# emotion_oid = "3a6f2751-1ba1-46cc-93ce-6d6531190c95" # Trump Rich
# emotion_oid = "d8ae7245-0347-4ad9-897e-2d50e5dbb7d9" # Trump Make America Great Again
# emotion_oid = "404c4da9-cbaa-4b87-941c-0dec227106fc" # e
# emotion_oid = "c3706363-9a1e-4341-8369-8b5ff90840a1" # e and her sis


emotion_oid = "9f7c7bc6-63f9-4305-b574-9c299ee331b2" # happy

results_em = get_emotion_results(emotion_oid, _emotion_key)

# with open('em_civil_war.txt', 'w') as outfile:
#     json.dump(results_em, outfile)

fragments_em_json = json.loads(results_em["processingResult"])

vid_width = fragments_em_json["width"]
vid_height = fragments_em_json["height"]
timescale = fragments_em_json["timescale"]
framerate = fragments_em_json["framerate"]

emotions = []

for fragment in fragments_em_json["fragments"]:

    curr_frame = fragment["start"]/timescale * framerate

    if curr_frame == len(emotions):
        try:
            emotions += fragment["events"]
        except KeyError:
            pass

    else:
        diff = curr_frame - len(emotions)
        emotions += [[] for i in range(int(diff))]

        try:
            emotions += fragment["events"]
        except KeyError:
            pass

cap = cv2.VideoCapture(video_path)
i = 0

while cap.isOpened():
    ret, frame = cap.read()

    time.sleep(1/framerate)

    if isinstance(frame, type(None)):
        break

    try:
        result_em = emotions[i]
        render_emotion_result_video(result_em, frame, vid_width, vid_height)
    except:
        print i
        pass

    cv2.imshow('frame', frame)

    i += 1

    if (cv2.waitKey(1) & 0xFF == ord('q')) or frame.size == 0:
        break

cap.release()
cv2.destroyAllWindows()

