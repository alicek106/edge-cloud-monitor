import time
import influxdb_query
import logging
print('########## monitoring data provider start! ###########')

#Logging setting
logging.basicConfig(level=logging.INFO)

print('## print All Node Network Bytes ##')
print(influxdb_query.getAllNodeNetworkBytes())
print('\n## print Each Node Network Bytes ##')
print(influxdb_query.getEachNodesNetworkBytes())
print('\n## print Each Service Network Bytes ##')

print(influxdb_query.getEachServiceNetworkBytes())
print('\n## print All Node Memory Percent ##')
print(influxdb_query.getAllNodesMemoryPercent())
print('\n## print Each Node Memory Percent ##')
print(influxdb_query.getEachNodesMemoryPercent())
print('\n## print Each Service Memory Percent ##')
print(influxdb_query.getEachServiceMemoryPercent())

print('\n## print All Node CPU Percent ##')
print(influxdb_query.getAllNodesCpuPercent())
print('\n## print Each Node CPU Percent ##')
print(influxdb_query.getEachNodesCpuPercent())
print('\n## print Each Service CPU Percent ##')
print(influxdb_query.getEachServiceCpuPercent())

