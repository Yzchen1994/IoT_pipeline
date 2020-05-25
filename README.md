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
