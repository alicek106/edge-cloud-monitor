import time
import influxdb_query
import logging
print('########## monitoring data provider start! ###########')

#Logging setting
logging.basicConfig(level=logging.INFO)

print(influxdb_query.getAllNodeNetworkBytes())
print(influxdb_query.getEachNodesNetworkBytes())
print(influxdb_query.getAllNodesMemoryPercent())
print(influxdb_query.getEachNodesMemoryPercent())
print(influxdb_query.getAllNodesCpuPercent())
print(influxdb_query.getEachNodesCpuPercent())
