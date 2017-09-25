import random
import time
import datetime
import json
import requests
import zlib

#SERVER_CERTS = '/home/felipe/ssl/XX.cert.pem' #Server_autorization
URL = "hKttps://sensingbus.gta.ufrj.br/zip_measurements_batch_sec/"
STOP_ID = 1

PRIMARY_KEY='/home/felipe/ssl/raspberry3.key.pem'
LOCAL_CERTIFICATE='/home/felipe/ssl/raspberry3.cert.pem'

random.seed(time.time())

message = {}

class Data:
    def __init__(self):
        self.datetime = str(datetime.datetime.now().strftime('%d%m%y%H%M%S%f'))[0:12] + '00'
        self.latitude = random.uniform(-22.3,-22.6)
        self.longitude = random.uniform(-43.3,-43.6)
        self.light = random.randint (997,999)
        self.temperature = random.uniform(20.0, 50.0)
        self.humidity = random.uniform (28.0, 31.0)
        self.rain = random.randint (774, 781)

def createMessage():
    message["stop_id"] = STOP_ID
    message["batches"] = []
    sensingMessage = {}
    dataLine = []
    data = []

    for sensingNode in range (1, 2):
        sensingMessage["node_id"] = sensingNode
        sensingMessage["type"] = 'data'
        sensingMessage["received"] = str(datetime.datetime.now().strftime('%d%m%y%H%M%S%f'))[0:12] + '00'
        sensingMessage["header"] = "datetime,lat,lng,light,temperature,humidity,rain"

        for line in range (0, 1):
            data.append(Data ())
            dataLine.append(str(data[line].datetime) + ',' + str(data[line].latitude) + ',' + str(data[line].longitude) + ',' + str(data[line].light) + ',' + str(data[line].temperature) + ',' + str(data[line].humidity) + ',' + str(data[line].rain))
        sensingMessage["load"] = dataLine
        data = []

        message['batches'].append(sensingMessage)

def doPOST (message):
        #print 'MENSAGEM COMPRIMIDA'
        #print message
        headers = {'Content-Encoding':'text/plain','Content-Length':str(len(message))}
        r = requests.post('%s'%URL, data=message,headers=headers,cert=(LOCAL_CERTIFICATE, PRIMARY_KEY))
        print r.text
        #print r.json
        #print r

if __name__ == "__main__":
    createMessage ()
    message = zlib.compress(json.dumps(message).encode('utf-8').encode('zlib_codec'), 9)
    #print message
    doPOST(message)
