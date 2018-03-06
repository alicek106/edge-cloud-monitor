import time
import influxdb_query
import logging
print('\n')
print('########## monitoring data provider start! ###########')

#Logging setting
logging.basicConfig(level=logging.INFO)

while True:
    time.sleep(2)
    influxdb_query.getAllServiceMemorySum()
