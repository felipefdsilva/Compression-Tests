import random
import time

random.seed(time.time())

class Data:
    def __init__(self):
        self.latitude = random.uniform(-22.3,-22.6)
        self.longitude = random.uniform(-43.3,-43.6)
        self.light = random.uniform (997,999)
        self.temperature = random.uniform(20.0, 50.0)
        self.humidity = random.uniform (28.0, 31.0)
        self.rain = random.uniform (774, 781)

def createSensingPost (data, line):
    data.append(Data ())
    #print '[',data.latitude,',',data.longitude,',',data.light,',',data.temperature,',',data.humidity,',',data.rain,']'

i = 0
data = []
while (i < 20):
    createSensingPost(data, i)
    dataLine = '['+ str(data[i].latitude) + ',' + str(data[i].longitude) + ',' + str(data[i].light) + ',' + str(data[i].temperature) + ',' + str(data[i].humidity) + ',' + str(data[i].rain) + ']'
    i+=1
    print dataLine
