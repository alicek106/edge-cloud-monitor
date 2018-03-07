# Docker Swarm Mode Monitoring : ICNS edge-cloud-monitor

First of all, you have to set up swarm mode cluster.  
And in all nodes (manager, worker) following option must be applied to Docker Daemon.  

### Docker Daemon Setup
#### 1. Setting Docker Daemon Option
```
bash# vim /etc/default/docker

DOCKER_OPTS="-H 0.0.0.0:2375 -H unix:///var/run/docker.sock"
```
In raspberry pi 3, follwing line must be added in /lib/systemd/system/docker.service
```
bash# vim /lib/systemd/system/docker.service

...
ExecStart=/usr/bin/dockerd -H fd:// $DOCKER_OPTS
EnvironmentFile=-/etc/default/docker
...
```
```
bash# systemctl daemon-reload
bash# service docker restart
```
  
### Python Environment setup
#### 2. apt update and install pip3
```
bash# apt update && apt install python3-pip -y
```

#### 3. install virtualenv
```
bash# pip3 install virtualenv
bash# cd /root
bash# git clone https://github.com/alicek106/edge-cloud-monitor.git
bash# cd edge-cloud-monitor/
bash# virtualenv icns
bash# source icns/bin/activate
bash# pip3 install docker influxdb
```
  
### Monitoring setup
#### 4. Monitoring System Deployment
In x86_64 CPU, follwing command will be used.
```
docker stack deploy -c docker-compose/docker-compose.yml monitoring
```
In ARM CPU, follwing command will be used.
```
bash# docker stack deploy -c docker-compose/docker-compose-arm.yml monitoring
```
After finishing launching all services, create cadvisor database in influxdb.
```
bash# docker exec `docker ps | grep -i influxdb | awk '{print $1}'` influx -execute 'CREATE DATABASE cadvisor'
```
  
### Config Settings
#### 5. Set up config files
Modify each ini files.
```
bash# vi influxdb_config.ini

[INFLUXDB]
INFLUX_HOST = 192.168.0.84
INFLUX_PORT = 8086
INFLUX_USER = root
INFLUX_PASSWORD = root
INFLUX_DB = cadvisor
```
  
```
bash# vi nodes_config.ini

rasp03 192.168.0.84:2375
rasp04 192.168.0.71:2375
rasp05 192.168.0.85:2375
```

#### Let's enjot monitoring !
```
bash# watch python3 edge-cloud-monitor.py
```
