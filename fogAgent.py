#Authors: Roberto Goncalves Pacheco e Felipe Ferreira da Silva
#Universidade do Estado do Rio de Janeiro
#Universidade Federal do Rio de Janeiro
#Departamento de Eletronica e Telecomunicacoes (UERJ)
#Departamento de Engenharia Eletrônica e de Computação (UFRJ)
#Project: Sensing Bus
#Subject: Comunication between Cloud and Fog

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import threading, Queue
import time
import datetime
import json
import requests
import zlib

STOP_ID = 1
URL = "https://sensingbus.gta.ufrj.br/zip_measurements_batch_sec/"
PRIMARY_KEY='/home/felipe/ssl/raspberry3.key.pem'
LOCAL_CERTIFICATE='/home/felipe/ssl/raspberry3.cert.pem'
COMPRESSION_LEVEL=9
WORD_SIZE_BITS=-15
MEM_LEVEL=9

queue = Queue.Queue()

def cloud_client(payload):
    """ Sends mensage to Cloud"""
    headers = {'Content-Encoding':'text/plain','Content-Length':str(len(message))}
    r = requests.post('%s'%URL, data=payload,headers=headers,cert=(LOCAL_CERTIFICATE, PRIMARY_KEY))
    #print r.text
    #print r.json
    print r

def compressMessage (size1, size2, t1, t2, message):
    """Compress Fog Message"""
    compressOBJ = zlib.compressobj(COMPRESSION_LEVEL, zlib.DEFLATED, WORD_SIZE_BITS, MEM_LEVEL, zlib.Z_FILTERED)
    compressOBJ.flush(zlib.Z_SYNC_FLUSH)

    size1 = len(message)
    t1 = time.time()

    messageText = compressOBJ.compress(message)
    messageText += compressOBJ.flush(zlib.Z_SYNC_FLUSH)

    t2 = time.time()
    size2 = len (messageText)

    return message

def createFogMessage(queue):
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
            message = compressMessage (size1, size2, t1, t2, output)
            print "Medidas", i, "\t", "Tempo", (t2-t1)*1000, "ms\t", "Razao Tamanho(bytes):", "%.0f" %((float(size2)/float(size1))*100),"%"
            cloud_client(message)
        time.sleep(30)

class Server(BaseHTTPRequestHandler):
    def createHeader(self):
        """Creates header HTTP requisition"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def readSensingNodeMessage(self):
        """Receives data from Arduino"""
    	input_batches = {}
    	postvars = parse_qs(self.rfile.read(int(self.headers['Content-Length'])), keep_blank_values=1)

        input_batches['node_id'] = postvars['node_id'][0]
        input_batches['type'] = str(postvars['type'][0])
        input_batches['header'] = str(postvars['header'][0])
        input_batches['received'] = str(datetime.datetime.now())
    	for line in postvars['load']:
        	tmp = line.split('\n')
        input_batches['load'] = tmp[0:-1] #the last line is always empty

        q.put(input_batches)
        return

def run(server_class=HTTPServer, handler_class=Server, port=50000):
    """Generates a server to receive POST method"""
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting Server Http'
    t = threading.Thread(target = createFogMessage, args=('alt',q))
    t.daemon = True
    t.start()
    httpd.serve_forever()
    t.join()

if __name__ == "__main__":
    run()
