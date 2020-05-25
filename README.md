# Configure networks
## Create a bridge:
```
docker network create --driver bridge hw03
```

# Spin up the face detector docker image
```
docker build -t cv2 -f Dockerfile.cv2 .
docker run -e DISPLAY=$DISPLAY --privileged --name cv2 --network hw03 -v /home/nvidia/Desktop/hw3:/hw3 -ti cv2
```

# Spin up MQTT broker 
```
docker build -t mqttbroker -f Dockerfile.mqttbroker .
docker run --name mqttbroker --network hw03 -p 1883:1883 -v /home/nvidia/Desktop/hw3:/hw3 --rm -ti mqttbroker
```

# Spin up MQTT Forwarder
## Docker setup
```
docker build -t mqttforwarder -f Dockerfile.mqttforwarder .
docker run --name mqttforwarder --network hw03 -v /home/nvidia/Desktop/hw3:/hw3 -ti mqttforwarder
```
## Run mqttforwarder.py
```
cd /hw3
python3 mqttforwarder.py
```

# Useful tools
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
docker run --name mqttbroker --network hw03 -p 1883:1883 -v /home/root/IoT_pipeline:/hw3 --rm -ti mqttbroker
```
