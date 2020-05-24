import numpy as np
import cv2
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# 1 should correspond to /dev/video1 , your USB camera. The 0 is reserved for the TX2 onboard camera
cap = cv2.VideoCapture(0)
print(face_cascade)

while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()

	# We don't use the color information, so might as well save space
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	# face detection and other logic goes here
	faces = face_cascade.detectMultiScale(gray, 1.3, 5)
	for (x,y,w,h) in faces:
		print("x, y, w, h = ", x, y, w, h)
		# cut out face from the frame.. 
		face_gray = gray[y:y+h, x:x+w]
		rc,png = cv2.imencode('.png', face_gray)
		msg = png.tobytes()
		# print('png bytes:', msg)
		# Send to MQTT forwarder. 		
		# remote_mqttclient.publish(REMOTE_MQTT_TOPIC, payload=msg, qos=0, retain=False)
