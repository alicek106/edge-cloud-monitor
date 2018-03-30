from influxdb import InfluxDBClient
import docker_node_spec
import json
import configparser

# Get Nodes Spec (CPU, Memory) but actually cpu value is not used
node_spec = docker_node_spec.getNodeSpec(docker_node_spec.getNodeInfo())
cpu_sum = 0
memory_sum = 0
for spec in node_spec:
    cpu_sum = cpu_sum + spec[2]
    memory_sum = memory_sum + spec[3]

# InfluxDB Connection Information
config = configparser.ConfigParser()
config.read('influxdb_config.ini')

influx_host=config['INFLUXDB']['INFLUX_HOST']
influx_port=config['INFLUXDB']['INFLUX_PORT']
influx_user = config['INFLUXDB']['INFLUX_USER']
influx_password = config['INFLUXDB']['INFLUX_PASSWORD']
influx_dbname = config['INFLUXDB']['INFLUX_DB']

## Query
get_all_nodes_memory_query = 'select "container_name", "com.docker.stack.namespace", "machine", ' \
    '"com.docker.swarm.service.name", "com.docker.swarm.task.name", ' \
    'last(value) from memory_rss where container_name != \'/\' and time > now() - 30s group by container_name;'

get_all_nodes_cpu_query = 'SELECT time, container_name, machine, "com.docker.swarm.service.name", value FROM cpu_usage_total ' \
    'where container_name != \'/\' and time > now() - 30s GROUP BY container_name ORDER BY DESC LIMIT 2'

get_all_nodes_rx_query = 'SELECT time, machine, container_name, "com.docker.swarm.service.name", value FROM rx_bytes where container_name != \'/\'  and time > now() - 30s GROUP BY container_name ORDER BY DESC LIMIT 2'
get_all_nodes_tx_query = 'SELECT time, machine, container_name, "com.docker.swarm.service.name", value FROM tx_bytes where container_name != \'/\' and time > now() - 30s GROUP BY container_name ORDER BY DESC LIMIT 2'



################### Memory
################### ... Memory!
 
def getAllNodesMemoryPercent():
    client = InfluxDBClient(influx_host, influx_port, influx_user, influx_password, influx_dbname)
    result = client.query(get_all_nodes_memory_query)
    points = list(result.get_points(measurement='memory_rss'))
    using_memory_sum = 0
    for point in points:
        data = point['last']/1024/1024
        using_memory_sum = using_memory_sum + point['last']
    dataDic = {'memory_usage_rss_total':round((using_memory_sum / 1024 / 1024 / memory_sum) * 100, 2)}
    client.close()
    return json.dumps(dataDic)

def getEachNodesMemoryPercent():
    client = InfluxDBClient(influx_host, influx_port, influx_user, influx_password, influx_dbname)
    result = client.query(get_all_nodes_memory_query)
    points = list(result.get_points(measurement='memory_rss'))

    dataDic = {}
    
    for spec in node_spec:
        dataDic[spec[0]] = 0
        
    for point in points:
        data = point['last'] / 1024 / 1024
        dataDic[point['machine']] = dataDic[point['machine']] + data

    for key in dataDic:
        dataDic[key] = round(dataDic[key] / spec[3] * 100, 2)
    
    client.close()
    return json.dumps(dataDic)

def getEachServiceMemoryPercent():
    client = InfluxDBClient(influx_host, influx_port, influx_user, influx_password, influx_dbname)
    result = client.query(get_all_nodes_memory_query)
    points = list(result.get_points(measurement='memory_rss'))

    dataDic = {}

    for point in points:
        data = point['last'] / 1024 / 1024
        try:
            dataDic[point['com.docker.swarm.service.name']] = dataDic[point['com.docker.swarm.service.name']] + data
        except:
            dataDic[point['com.docker.swarm.service.name']] = data

    for key in dataDic:
        dataDic[key] = round(dataDic[key] / spec[3] * 100, 2)

    return json.dumps(dataDic)

################### CPU 
################### ... CPU!

def getAllNodesCpuPercent():
    client = InfluxDBClient(influx_host, influx_port, influx_user, influx_password, influx_dbname)
    result = client.query(get_all_nodes_cpu_query, epoch='ns')
    points = list(result.get_points(measurement='cpu_usage_total'))

    using_cpu_percent_sum = 0
    index = True # variable for switch. Because query return each 2 rows...
    time = 0 # Temp variable for saving time
    cpu_accumulative = 0 # Temp variable for saving accumulative value

    for point in points:
        if(index):
            time = point['time']
            cpu_accumulative = point['value']
            index = False
        else:
            using_cpu_percent_sum = using_cpu_percent_sum + (((cpu_accumulative - point['value']) / (time - point['time']))*100)
            index = True
    dataDic = {'cpu_usage_total': round(using_cpu_percent_sum, 2)}
    client.close()
    return json.dumps(dataDic)

def getEachNodesCpuPercent():
    client = InfluxDBClient(influx_host, influx_port, influx_user, influx_password, influx_dbname)
    result = client.query(get_all_nodes_cpu_query, epoch='ns')
    points = list(result.get_points(measurement='cpu_usage_total'))
    index = True # variable for switch. Because query return each 2 rows...
    time = 0 # Temp variable for saving time
    cpu_accumulative = 0 # Temp variable for saving accumulative value
    
    dataDic = {}
    dataArr = []

    for spec in node_spec:
        dataDic[spec[0]] = 0
        
    for point in points:
        if(index):
            time = point['time']
            cpu_accumulative = point['value']
            index = False
        else:
            dataDic[point['machine']] = dataDic[point['machine']] + (((cpu_accumulative - point['value']) / (time - point['time']))*100)
            index = True

    for key in dataDic:
        dataDic[key] = round(dataDic[key], 2)

    client.close()
    return json.dumps(dataDic)

def getEachServiceCpuPercent():
    client = InfluxDBClient(influx_host, influx_port, influx_user, influx_password, influx_dbname)
    result = client.query(get_all_nodes_cpu_query, epoch='ns')
    points = list(result.get_points(measurement='cpu_usage_total'))
    index = True # variable for switch. Because query return each 2 rows...
    time = 0 # Temp variable for saving time
    cpu_accumulative = 0 # Temp variable for saving accumulative value

    dataDic = {}

    for point in points:
        if(index):
            time = point['time']
            cpu_accumulative = point['value']
            index = False
        else:
            try:
                dataDic[point['com.docker.swarm.service.name']] = dataDic[point['com.docker.swarm.service.name']] + (((cpu_accumulative - point['value']) / (time - point['time']))*100)
            except:
                dataDic[point['com.docker.swarm.service.name']] = (((cpu_accumulative - point['value']) / (time - point['time']))*100)
            index = True

    for key in dataDic:
        dataDic[key] = round(dataDic[key], 2)

    client.close()
    return json.dumps(dataDic)

######## Network
######## ... Network!

def getAllNodeNetworkBytes():
    client = InfluxDBClient(influx_host, influx_port, influx_user, influx_password, influx_dbname)

    ######## Rx Bytes
    result = client.query(get_all_nodes_rx_query, epoch='ns')
    points = list(result.get_points(measurement='rx_bytes'))
    used_rx_bytes = 0
    index = True # variable for switch. Because query return each 2 rows...
    time = 0 # Temp variable for saving time
    rx_accumulative = 0 # Temp variable for saving accumulative value

    for point in points:
        if(index):
            time = point['time']
            rx_accumulative = point['value']
            index = False
        else:
            used_rx_bytes = used_rx_bytes + (rx_accumulative - point['value'])
            index = True

    ######## Tx Bytes
    result = client.query(get_all_nodes_tx_query, epoch='ns')
    points = list(result.get_points(measurement='tx_bytes'))
    used_tx_bytes = 0
    index = True # variable for switch. Because query return each 2 rows...
    time = 0 # Temp variable for saving time
    tx_accumulative = 0 # Temp variable for saving accumulative value

    for point in points:
        if(index):
            time = point['time']
            tx_accumulative = point['value']
            index = False
        else:
            used_tx_bytes = used_tx_bytes + (tx_accumulative - point['value'])
            index = True

    dataDic = {'rx_byte_total': used_rx_bytes, 'tx_byte_total': used_tx_bytes}
    client.close()
    return json.dumps(dataDic)


def getEachNodesNetworkBytes():
    client = InfluxDBClient(influx_host, influx_port, influx_user, influx_password, influx_dbname)

    ######## Rx Bytes
    result = client.query(get_all_nodes_rx_query, epoch='ns')
    points = list(result.get_points(measurement='rx_bytes'))
    used_rx_bytes = 0
    index = True # variable for switch. Because query return each 2 rows...
    time = 0 # Temp variable for saving time
    rx_accumulative = 0 # Temp variable for saving accumulative value

    dataDic_Rx = {}
    
    for spec in node_spec:
        dataDic_Rx[spec[0]] = 0
        
    for point in points:
        if(index):
            time = point['time']
            rx_accumulative = point['value']
            index = False
        else:
            dataDic_Rx[point['machine']] = dataDic_Rx[point['machine']] + (rx_accumulative - point['value'])
            index = True

    ######## Tx Bytes
    result = client.query(get_all_nodes_tx_query, epoch='ns')
    points = list(result.get_points(measurement='tx_bytes'))
    used_tx_bytes = 0
    index = True # variable for switch. Because query return each 2 rows...
    time = 0 # Temp variable for saving time
    tx_accumulative = 0 # Temp variable for saving accumulative value

    dataDic_Tx = {}
    
    for spec in node_spec:
        dataDic_Tx[spec[0]] = 0
        
    for point in points:
        if(index):
            time = point['time']
            tx_accumulative = point['value']
            index = False
        else:
            dataDic_Tx[point['machine']] = dataDic_Tx[point['machine']] + (tx_accumulative - point['value'])
            index = True
            
    ## integrate!
    dataArr = []
    for spec in node_spec:
        tmpDataDic = {'host' : spec[0], 'rx_byte' : dataDic_Rx[spec[0]], 'tx_byte': dataDic_Tx[spec[0]]}
        dataArr.append(tmpDataDic)
        
    return json.dumps(dataArr)

def getEachServiceNetworkBytes():
    client = InfluxDBClient(influx_host, influx_port, influx_user, influx_password, influx_dbname)

    ######## Rx Bytes
#    result = client.query(get_all_nodes_rx_query, epoch='ns')
    result = client.query(get_all_nodes_rx_query)
    points = list(result.get_points(measurement='rx_bytes'))
    used_rx_bytes = 0 
    index = True # variable for switch. Because query return each 2 rows...
    time = 0 # Temp variable for saving time
    rx_accumulative = 0 # Temp variable for saving accumulative value

    dataDic_Rx = {}
    
    for point in points:
        if(index):
            time = point['time']
            rx_accumulative = point['value']
            index = False
        else:
            try:
                dataDic_Rx[point['com.docker.swarm.service.name']] = dataDic_Rx[point['com.docker.swarm.service.name']] + (rx_accumulative - point['value'])
            except:
                dataDic_Rx[point['com.docker.swarm.service.name']] = (rx_accumulative - point['value'])
            index = True

    ######## Tx Bytes
    result = client.query(get_all_nodes_tx_query, epoch='ns')
    points = list(result.get_points(measurement='tx_bytes'))
    used_tx_bytes = 0 
    index = True # variable for switch. Because query return each 2 rows...
    time = 0 # Temp variable for saving time
    tx_accumulative = 0 # Temp variable for saving accumulative value

    dataDic_Tx = {}

    for point in points:
        if(index):
            time = point['time']
            tx_accumulative = point['value']
            index = False
        else:
            try:
                dataDic_Tx[point['com.docker.swarm.service.name']] = dataDic_Tx[point['com.docker.swarm.service.name']] + (tx_accumulative - point['value'])
            except:
                dataDic_Tx[point['com.docker.swarm.service.name']] = (tx_accumulative - point['value'])
            index = True

    ## integrate!
    dataArr = []
    for key in dataDic_Tx:
        tmpDataDic = {'service' : key, 'rx_byte' : dataDic_Rx[key], 'tx_byte': dataDic_Tx[key]}
        dataArr.append(tmpDataDic)

    return json.dumps(dataArr)

#print(getAllNodeNetworkBytes())
#print(getEachNodesNetworkBytes())
#print(getAllNodesMemoryPercent())
#print(getEachNodesMemoryPercent())
#print(getAllNodesCpuPercent())
#print(getEachNodesCpuPercent())
