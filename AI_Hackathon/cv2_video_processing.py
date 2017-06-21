import cv2
from emotions_api import _key
from emotions_api.make_call_photo import render_result, process_request

headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': _key,
        'Content-Type': 'application/octet-stream'
    }

cap = cv2.VideoCapture('videos/sad.mp4')

while cap.isOpened():
    ret, frame = cap.read()

    data = cv2.imencode('.jpg', frame)[1].tostring()

    result = process_request(None, data, headers, None)

    if result is not None:
        # Load the original image, fetched from the URL
        arr = frame
        render_result(result, frame)

    cv2.imshow('frame', frame)

    if cv2.waitKey(500) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()