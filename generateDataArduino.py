import random
import time
import datetime
import json
import requests
import zlib

#URL = "https://sensingbus.gta.ufrj.br/zip_measurements_batch_sec/"
URL = "192.168.0.1"
#STOP_ID = 1
#PRIMARY_KEY='/home/felipe/ssl/raspberry3.key.pem'
#LOCAL_CERTIFICATE='/home/felipe/ssl/raspberry3.cert.pem'
NUMBER_GATHERING=2
MAX_SENSING_NODES=1
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

def createMessage(message, max_sensing_nodes, data):

    for sensingNode in range (0, max_sensing_nodes):
        message["node_id"] = sensingNode+1
        message["type"] = 'data'
        message["received"] = str(datetime.datetime.now().strftime('%d%m%y%H%M%S%f'))[0:12] + '00'
        message["header"] = "datetime,lat,lng,light,temperature,humidity,rain"
        message["load"] = data

    return message

def doPOST (message):
        headers = {'Content-Type':'application/x-www-form-urlencoded','Content-Length':str(len(message))}
        r = requests.post('%s'%URL, data=message,headers=headers)
        return r.text
        #return r.json
        #return r

if __name__ == "__main__":
    message = {}
    messageText = ""

    #print "Numero de Arduinos: ", MAX_SENSING_NODES

    for i in [1, 10, 100, 1000, 10000]:
        data = generateData (i)
        message = createMessage (message, MAX_SENSING_NODES, data)
        messageText = json.dumps(message)

    #print messageText
    print doPOST(messageText)
