# HW 3 Overview
In this homework, there are 3 docker images built on Jetson TX2: cv2, mqttbroker, mqttforwarder. cv2 is used to process face detection from a live camera stream. The detected face images are sent to mqttforwarder via mqttbroker through topic "face_detection_topic". The mqttforwarder then pass the binary image to cloud. 

There are 2 containers set up on the IBM cloud: mqttbrokerserver, imageprocessorserver. The binary image from Jetson TX2 are passed to imageprocessorserver via mqttbrokerserver through the topic "face_detection_topic". Once imageprocessorserver received the image, it will sent to IBM Object Storage by using the FUSE mounted drive on the container. 

# Object Storage Bucket URL
```
http://s3.us-east.cloud-object-storage.appdomain.cloud/cloud-object-storage-sj-cos-standard-qpp/
```

# Setup on Jetson TX2
## Configure networks:
```
docker network create --driver bridge hw03
```

## Spin up the face detector docker image
```
docker build -t cv2 -f Dockerfile.cv2 .
docker run -e DISPLAY=$DISPLAY --privileged --name cv2 --network hw03 -v /home/nvidia/Desktop/hw3:/hw3 -ti cv2
```

## Spin up MQTT broker 
```
docker build -t mqttbroker -f Dockerfile.mqttbroker .
docker run --name mqttbroker --network hw03 -p 1883:1883 -v /home/nvidia/Desktop/hw3:/hw3 --rm -ti mqttbroker
```

## Spin up MQTT Forwarder
### Docker setup
```
docker build -t mqttforwarder -f Dockerfile.mqttforwarder .
docker run --name mqttforwarder --network hw03 -v /home/nvidia/Desktop/hw3:/hw3 -ti mqttforwarder
```
### Run mqttforwarder.py
```
cd /hw3
python3 mqttforwarder.py
```

# Cloud configuration
## Spin up a cloud instance on IBM Cloud
```
ssh root@<ibm-ip-address>
ibmcloud sl vs create --datacenter=wdc07 --domain=hw03.UC-Berkeley.cloud --hostname=hw03 --os=UBUNTU_18 --cpu=2 --memory=2048 --disk=100 --billing=hourly --key=1809990
```

## After the new instance is ready
```
ssh root@169.62.41.122
git clone git@github.com:Yzchen1994/IoT_pipeline.git
```

## Install docker in the cloud
```
apt-get update
apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
    
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

apt-get update
apt-get install docker-ce
```

## Create a bridge:
```
docker network create --driver bridge hw03
```

## Spin up MQTT broker on the cloud
```
docker build -t mqttbroker -f Dockerfile.mqttbrokerserver .
docker run --name mqttbroker --network hw03 -p 1883:1883 -v /root/IoT_pipeline:/hw3 --rm -ti mqttbroker
```

## Spin up Image Processor on the cloud
```
docker build -t imageprocessor -f Dockerfile.imageprocessorserver .
docker run --name imageprocessor --network hw03 -v /root/IoT_pipeline:/hw3 --priviledged -ti imageprocessor
```

Setup s3fs
In order to configure s3fs-fuse, you need your access key id, your secret access key, the name of the bucket you want to mount, and the endpoint for the If you are using the Infrastructure variation of Cloud Object Storage (i.e. softlayer), you can get these values from the ObjectStorage section in the Control Portal. If you are using the new version of IBM Cloud Object storage, you will need to go to Service Credentials, New Credential (be sure to check the HMAC checkbox), and then click "view credential". You will see a JSON file, so just look for the cos_hmac_keys section:
```
#   "cos_hmac_keys": {
#    "access_key_id": "somekey",
#    "secret_access_key": "somesecretkey"
#  },
```

Substitue your values for <Access_Key_ID> and <Secret_Access_Key> in the below command.
```
echo "<Access_Key_ID>:<Secret_Access_Key>" > $HOME/.cos_creds
chmod 600 $HOME/.cos_creds
```

Create a directory where you can mount your bucket. Typically, this is done in the /mnt directory on Linux, notice the bucket is created in the IBM Cloud UI
```
mkdir -m 777 /mnt/mybucket
s3fs cloud-object-storage-sj-cos-standard-qpp /mnt/mybucket -o passwd_file=$HOME/.cos_creds -o sigv2 -o use_path_request_style -o url=https://s3.us-east.cloud-object-storage.appdomain.cloud

```

Run processor
```
cd /hw3
python3 image_processor_cloud.py
```

# Useful Docker Commands
## Stop all running containers
```
docker stop $(docker ps -aq)
```

## Remove all containers
```
docker rm $(docker ps -aq)
```

## Remove network
```
docker network rm hw03
```

## Force stop 1883 port
```
fuser -k 1883/tcp
```

