import docker
import logging

# Config load (Docker Configs)
def getNodeInfo():
    loader = open("nodes_config.ini", 'r')
    nodes_info = []
        
    lines = loader.readlines()
    for line in lines:
        line = line.rstrip('\n')
        node_info = [line.split(' ')[0], line.split(' ')[1]]
        nodes_info.append(node_info)
    loader.close()
	
    return nodes_info

# Return Docker Spec : Memory, CPU
def getNodeSpec(nodes_info):
    nodes_spec = []
    for node_info in nodes_info:
        client = docker.DockerClient(base_url=node_info[1])
        node_docker_info = client.info()

        MemTotal = round(node_docker_info['MemTotal'] / 1024 / 1024, 2)
        NCPU = node_docker_info['NCPU']
        node_spec = [node_info[0], node_info[1], NCPU, MemTotal]
        nodes_spec.append(node_spec)
    return nodes_spec   

#print(getNodeSpec(getNodeInfo()))
