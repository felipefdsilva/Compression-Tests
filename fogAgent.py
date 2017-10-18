# -*- coding: utf-8 -*-
#Authors: Roberto Goncalves Pacheco e Felipe Ferreira da Silva
#Universidade do Estado do Rio de Janeiro
#Universidade Federal do Rio de Janeiro
#Departamento de Eletronica e Telecomunicacoes (UERJ)
#Departamento de Engenharia Eletronica e de Computacao (UFRJ)
#Project: SensingBus
#Subject: Fog agent with compression

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import matplotlib.pyplot as plt
from urlparse import parse_qs
import threading, Queue
import Tkinter as tk
import datetime
import requests
import time
import json
import zlib
import sys

URL = "https://sensingbus.gta.ufrj.br/zip_measurements_batch_sec/"
LOCAL_CERTIFICATE='/home/felipe/ssl/raspberry3.cert.pem'
PRIMARY_KEY='/home/felipe/ssl/raspberry3.key.pem'
COMPRESSION_LEVEL=9
WORD_SIZE_BITS=-15
MEM_LEVEL=9
STOP_ID = 1

queue = Queue.Queue()
stats = {}
counter = 0

def increment():
    global counter
    counter += 1
    if (counter==100):
        counter = 1
    print counter
    return counter

def createGraphics ():
    dt = []
    sizeGain = []

    for key in stats.keys():
        dt.append(key)
        sizeGain.append(stats[key])

    print dt
    print sizeGain

    plt.figure()
    plt.plot(dt, sizeGain, '-+', markersize=13, markerfacecolor='k')
    plt.xlabel('(ms)')
    plt.ylabel('(%)')
    plt.title('Ganho de Tamanho x Tempo de Compressao')
    plt.grid(True)
    plt.savefig('stats.png')
    plt.close()
    return

def cloud_client(payload):
    """ Sends mensage to Cloud"""
    headers = {'Content-Encoding':'application/x-www-form-urlencoded','Content-Length':str(len(payload))}
    r = requests.post('%s'%URL, data=payload, headers=headers,cert=(LOCAL_CERTIFICATE, PRIMARY_KEY))
    #print r

def compressMessage (message):
    """Compress Fog Message"""
    compressOBJ = zlib.compressobj(COMPRESSION_LEVEL, zlib.DEFLATED, WORD_SIZE_BITS, MEM_LEVEL, zlib.Z_FILTERED)
    #compressOBJ.flush(zlib.Z_SYNC_FLUSH)

    messageText = json.dumps(message)
    size1 = len(messageText)
    messageText = messageText.encode('utf-8').encode('zlib_codec')

    t1 = time.time()
    messageText = compressOBJ.compress(messageText)
    messageText += compressOBJ.flush()
    t2 = time.time()

    size2 = len (messageText)

    deltat = "{:.2f}".format((t2-t1)*1000)
    sizeGain = "{:.0f}".format(float(size2)/float(size1)*100)
    stats[deltat] = (sizeGain)

    if (increment() == 99):
        createGraphics ()

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
            cloud_client(message)
            #time.sleep(1)

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
