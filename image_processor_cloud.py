# Run on cloud
import paho.mqtt.client as mqtt	
from datetime import datetime
import time
import numpy as np
import cv2

LOCAL_MQTT_HOST="mqttbroker"
LOCAL_MQTT_PORT=1883
LOCAL_MQTT_TOPIC="face_detection_topic"

MNT_PATH="/mnt/mybucket/"

def on_connect_local(client, userdata, flags, rc):
        print("connected to local broker with rc: " + str(rc))
        client.subscribe(LOCAL_MQTT_TOPIC)
	
def on_message(client,userdata, msg):
	try:
		print("message received!")	
		# if we wanted to re-publish this message, something like this should work
		msg = msg.payload
		
		# decode img (https://stackoverflow.com/questions/17170752/python-opencv-load-image-from-byte-string)
		nparr = np.fromstring(msg, np.uint8)
		img_np = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

		time_now = datetime.now()
		file_name = '{}.png'.format(time.time())
		file_path = MNT_PATH + file_name
		cv2.imwrite(file_path, img_np)
		print("successfully written to file:{}".format(file_name))
	except:
		print("Unexpected error:", sys.exc_info()[0])

local_mqttclient = mqtt.Client()
local_mqttclient.on_connect = on_connect_local
local_mqttclient.connect(LOCAL_MQTT_HOST, LOCAL_MQTT_PORT, 360)
local_mqttclient.on_message = on_message



# go into a loop
local_mqttclient.loop_forever()
