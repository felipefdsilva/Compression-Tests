import random
import time
import datetime
import json
import requests
import zlib

URL = "https://sensingbus.gta.ufrj.br/zip_measurements_batch_sec/"
STOP_ID = 1
PRIMARY_KEY='/home/felipe/ssl/raspberry3.key.pem'
LOCAL_CERTIFICATE='/home/felipe/ssl/raspberry3.cert.pem'
NUMBER_GATHERING=2
MAX_SENSING_NODES=2
COMPRESSION_LEVEL=9

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
    message["stop_id"] = STOP_ID
    message["batches"] = []
    sensingMessage = {}

    for sensingNode in range (1, max_sensing_nodes):
        sensingMessage["node_id"] = sensingNode
        sensingMessage["type"] = 'data'
        sensingMessage["received"] = str(datetime.datetime.now().strftime('%d%m%y%H%M%S%f'))[0:12] + '00'
        sensingMessage["header"] = "datetime,lat,lng,light,temperature,humidity,rain"
        sensingMessage["load"] = data

        message['batches'].append(sensingMessage)

    return message

# def doPOST (message):
#         headers = {'Content-Encoding':'text/plain','Content-Length':str(len(message))}
#         r = requests.post('%s'%URL, data=message,headers=headers,cert=(LOCAL_CERTIFICATE, PRIMARY_KEY))
#         print r.text
#         #print r.json
#         #print r

if __name__ == "__main__":
    message = {}
    messageText = ""
    print "Numero de Arduinos: ", MAX_SENSING_NODES
    for i in range (0, 1000000, 1000):
        data = generateData (i)
        createMessage (message, MAX_SENSING_NODES, data)
        t1 = time.time()
        messageText = zlib.compress(json.dumps(message).encode('utf-8').encode('zlib_codec'), COMPRESSION_LEVEL)
        t2 = time.time()
        print "Numero de medidas ", i
        print "Tempo de compressao: ", (t2-t1)*1000,"ms"
    #print messageText
    #doPOST(messageText)
