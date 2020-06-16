import numpy as np
import cv2
import paho.mqtt.client as mqtt
import tensorflow as tf
from tf_trt_models.detection import download_detection_model, build_detection_graph
import numpy as np
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Setup remote MQTT connection
REMOTE_MQTT_HOST="mqttbroker"
REMOTE_MQTT_PORT=1883
REMOTE_MQTT_TOPIC="face_detection_topic"
remote_mqttclient = mqtt.Client()
remote_mqttclient.connect(REMOTE_MQTT_HOST, REMOTE_MQTT_PORT, 360)

# 1 should correspond to /dev/video1 , your USB camera. The 0 is reserved for the TX2 onboard camera
cap = cv2.VideoCapture(0)
print(face_cascade)

# https://github.com/NVIDIA-AI-IOT/tf_trt_models/blob/master/tf_trt_models/detection.py
INPUT_NAME='image_tensor'
BOXES_NAME='detection_boxes'
CLASSES_NAME='detection_classes'
SCORES_NAME='detection_scores'
MASKS_NAME='detection_masks'
NUM_DETECTIONS_NAME='num_detections'
DETECTION_THRESHOLD = 0.5

input_names = [INPUT_NAME]
output_names = [BOXES_NAME, CLASSES_NAME, SCORES_NAME, NUM_DETECTIONS_NAME]


# Optimize the frozen graph using TensorRT
trt_graph = trt.create_inference_graph(
    input_graph_def=frozen_graph,
    outputs=output_names,
    max_batch_size=1,
    max_workspace_size_bytes=1 << 25,
    precision_mode='FP16',
    minimum_segment_size=50
)

tf_config = tf.ConfigProto()
tf_config.gpu_options.allow_growth = True

tf_sess = tf.Session(config=tf_config)

# use this if you want to try on the optimized TensorRT graph
# Note that this will take a while
# tf.import_graph_def(trt_graph, name='')

# use this if you want to try directly on the frozen TF graph
# this is much faster
tf.import_graph_def(frozen_graph, name='')

tf_input = tf_sess.graph.get_tensor_by_name(input_names[0] + ':0')
tf_scores = tf_sess.graph.get_tensor_by_name('detection_scores:0')
tf_boxes = tf_sess.graph.get_tensor_by_name('detection_boxes:0')
tf_classes = tf_sess.graph.get_tensor_by_name('detection_classes:0')
tf_num_detections = tf_sess.graph.get_tensor_by_name('num_detections:0')

while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()

	# We don't use the color information, so might as well save space
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	# face detection and other logic goes here
	# faces = face_cascade.detectMultiScale(gray, 1.3, 5)

	# Run network on image
	scores, boxes, classes, num_detections = tf_sess.run([tf_scores, tf_boxes, tf_classes, tf_num_detections], feed_dict={
	    tf_input: image_resized[None, ...]
	})

	boxes = boxes[0] # index by 0 to remove batch dimension
	scores = scores[0]
	classes = classes[0]
	num_detections = num_detections[0]

	fig = plt.figure()

	ax = fig.add_subplot(1, 1, 1)

	ax.imshow(image)

	# plot boxes exceeding score threshold
	for i in range(int(num_detections)):
	    if scores[i] < DETECTION_THRESHOLD:
	        continue
	    # scale box to image coordinates
	    box = boxes[i] * np.array([image.shape[0], image.shape[1], image.shape[0], image.shape[1]])

	    # display rectangle
	    patch = patches.Rectangle((box[1], box[0]), box[3] - box[1], box[2] - box[0], color='g', alpha=0.3)
	    ax.add_patch(patch)

	    # display class index and score
	    plt.text(x=box[1] + 10, y=box[2] - 10, s='%d (%0.2f) ' % (classes[i], scores[i]), color='w')

	plt.show()

	for (x,y,w,h) in faces:
		print("x, y, w, h = ", x, y, w, h)
		# cut out face from the frame.. 
		face_gray = gray[y:y+h, x:x+w]
		rc,png = cv2.imencode('.png', face_gray)
		msg = png.tobytes()
		# print('png bytes:', msg)
		# Send to MQTT forwarder. 		
		remote_mqttclient.publish(REMOTE_MQTT_TOPIC, payload=msg, qos=0, retain=False)
