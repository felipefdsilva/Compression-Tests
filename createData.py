#Authors: Felipe Ferreira da Silva
#Universidade Federal do Rio de Janeiro
#Departamento de Engenharia Eletronica e de Computacao (UFRJ)
#Project: SensingBus
#Subject: Comunication between Cloud and Fog

import random
import time
import datetime
import json
import requests
import zlib

URL = 'http://127.0.0.1:50000/'
NUMBER_GATHERING=20
NUMBER_SENSING_NODES=100
COMPRESSION_LEVEL=9
WORD_SIZE_BITS=-15
MEM_LEVEL=9

random.seed(time.time())

class Data:
    def __init__(self):
        self.datetime = datetime.datetime.now().strftime('%d%m%y%H%M%S')
        self.latitude = random.uniform(-22.3,-22.6)
        self.longitude = random.uniform(-43.3,-43.6)
        self.light = random.randint (997,999)
        self.temperature = random.uniform(20.0, 50.0)
        self.humidity = random.uniform (28.0, 31.0)
        self.rain = random.randint (774, 781)
        self.data = str(self.datetime) + '00' + ',' + str(self.latitude) + ',' + str(self.longitude) + ',' + str(self.light) + ',' + str(self.temperature) + ',' + str(self.humidity) + ',' + str(self.rain)

def generateData (max_gathering):
    dataList = []

    for line in range (0, max_gathering):
        dataList.append(Data().data)

    return dataList

def createMessage(sensing_node, data):
    message = {}

    message["node_id"] = sensing_node
    message["type"] = 'data'
    message["header"] = "datetime,lat,lng,light,temperature,humidity,rain"
    message["load"] = data

    return message

def doPOST (message):
        headers = {'Content-Type':'application/x-www-form-urlencoded','Content-Length':str(len(message))}
        r = requests.post('%s'%URL, data=message,headers=headers)
        return r

if __name__ == "__main__":
    data = []
    messageText = ""

    for sensingNode in range(1, NUMBER_SENSING_NODES+1):
        data = generateData (sensingNode)
        print doPOST(createMessage(sensingNode, data))
        #time.sleep(sensingNode)
