# -*- coding: utf-8 -*-
#Authors: Roberto Goncalves Pacheco e Felipe Ferreira da Silva
#Universidade do Estado do Rio de Janeiro
#Universidade Federal do Rio de Janeiro
#Departamento de Eletronica e Telecomunicacoes (UERJ)
#Departamento de Engenharia Eletronica e de Computacao (UFRJ)
#Project: SensingBus
#Subject: Fog agent with compression

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from scipy.interpolate import UnivariateSpline
from scipy.signal import lfilter
import matplotlib.pyplot as plt
from urlparse import parse_qs
import threading, Queue
import datetime
import requests
import time
import json
import zlib

#URL = "https://sensingbus.gta.ufrj.br/zip_measurements_batch_sec/"
URL = '127.0.0.01:50001'
LOCAL_CERTIFICATE='/home/felipe/ssl/raspberry3.cert.pem'
PRIMARY_KEY='/home/felipe/ssl/raspberry3.key.pem'
COMPRESSION_LEVEL=1
WORD_SIZE_BITS=-15
MAX_MEASURES=100
MEM_LEVEL=9
STOP_ID = 1
OFFSET=1

queue = Queue.Queue()
deltat = []
sizeGain = []

def createGraphics ():
    x_axis = range(OFFSET, 20*len(sizeGain)+OFFSET, 20)
    fig, sGPlot = plt.subplots()
    smooth_sizeGain = UnivariateSpline (x_axis, sizeGain)
    sGPlot.plot(x_axis, smooth_sizeGain(x_axis), 'b-')
    #sGPlot.plot(x_axis, sizeGain, 'b-')

    dtPlot = sGPlot.twinx()
    n = 1000  # the larger n is, the smoother curve will be
    b = [1.0 / n] * n
    smooth_deltat = lfilter(b, 1, deltat)
    dtPlot.plot(x_axis, smooth_deltat, 'r-')
    #dtPlot.plot(x_axis, deltat, 'r-')

    sGPlot.set_xlabel('(Numero de Tuplas)')
    sGPlot.set_ylabel('Reducao de Tamanho (%)', color='b')
    dtPlot.set_ylabel('Tempo de Compressao (ms)', color='r')

    fig.tight_layout()
    plt.show()
    plt.close()
    return

def cloud_client(payload):
    """ Sends mensage to Cloud"""
    headers = {'Content-Encoding':'application/plain-text','Content-Length':str(len(payload))}
    r = requests.post('%s'%URL, data=payload, headers=headers, cert=(LOCAL_CERTIFICATE, PRIMARY_KEY))
    return r.json

def compressMessage (message):
    """Compress Fog Message"""
    compressOBJ = zlib.compressobj(COMPRESSION_LEVEL, zlib.DEFLATED, WORD_SIZE_BITS, MEM_LEVEL, zlib.Z_HUFFMAN_ONLY)
    #compressOBJ.flush(zlib.Z_SYNC_FLUSH)

    messageText = json.dumps(message)
    print messageText
    size1 = float(len(messageText))
    messageText = messageText.encode('utf-8').encode('zlib_codec')

    t1 = time.time()
    messageText = compressOBJ.compress(messageText)
    messageText += compressOBJ.flush()
    t2 = time.time()

    size2 = float(len(messageText))
    dt = float("{:.2}".format((t2-t1)*1000))

    deltat.append(dt)
    sizeGain.append("{:.0f}".format(size2/size1*100))
    print "num medidas: ", len(deltat)
    if (len(deltat)==MAX_MEASURES):
        createGraphics ()
        del deltat[:]
        del sizeGain[:]

    return messageText

def createFogMessage(threat_name, queue):
    """Sends periodically stored data"""
    while True:
        output = {}
        output['stop_id'] = STOP_ID
        output['batches'] = []
        if not queue.empty():
            while not queue.empty():
                batch = queue.get()
                if (batch is not None):
                    output['batches'].append(batch)
            message = compressMessage (output)
            print cloud_client(message)
            time.sleep(30)

class Server(BaseHTTPRequestHandler):

    def do_POST(self):
        """Receives data from Arduino"""
        tmp = []
    	input_batches = {}
    	postvars = parse_qs(self.rfile.read(int(self.headers['Content-Length'])), keep_blank_values=1)
        input_batches['node_id'] = postvars['node_id'][0]
        input_batches['type'] = str(postvars['type'][0])
        input_batches['header'] = str(postvars['header'][0])
        input_batches['received'] = str(datetime.datetime.now().strftime('%d%m%y%H%M%S'))+'00'
        input_batches['load'] = postvars['load']
        queue.put(input_batches)
        self.send_response(200)
        return

def run(server_class=HTTPServer, handler_class=Server, port=50000):
    """Generates a server to receive POST method"""
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting Server Http'
    t = threading.Thread(target = createFogMessage, args=('alt', queue))
    t.daemon = True
    t.start()
    httpd.serve_forever()
    t.join()

if __name__ == "__main__":
    run()
