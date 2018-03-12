#!/usr/bin/env python


## Tiny Syslog Server Settings 

LOG_ENABLE = False          # Set to True if you want to enable Logging to LOG_FILE 
LOG_FILE = 'logfile.log'    # filename of Logging File 
HOST, PORT = "0.0.0.0", 514 # IP (0.0.0.0 : for all interfaces), UDP port setting (default UDP Port= 514)

propertyName = "TrapsEvents" # Property name to be used in FS Web-Service Composite Property 

### You need to create a Web-Service Property in your ForeScout CounterACT / Data-Exchange DEX / Web-Services Properties 
### Property Name: should match above - default "TrapsEvents" - Type Composite 
### Sample Composite property XML is provided which includes the following properties: 
#### TimeStamp (String) - Inv 
#### Source (String) - Inv 
#### Type (String) - Inv 
#### Content (String) - Inv 
#### Message (String) 

#
# NO USER SERVICEABLE PARTS BELOW HERE...
#

import logging
import SocketServer
import threading
from pyFS import pyFS
import warnings; warnings.simplefilter('ignore')
fs = pyFS()

logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filename=LOG_FILE, filemode='a')

def eventToObj(msg, obj):
    tmsg =msg.split(',')
    if len(tmsg) > 15:
        TargetIP = tmsg[13]
        tmp = tmsg[0].split("- - -")
        obj["TimeStamp"] = tmp[1].strip()
        obj["Source"] = "%s:%s:%s" % (tmsg[1], tmsg[2], tmsg[9])
        obj["Type"] = "%s:%s" %(tmsg[3], tmsg[4]) 
        obj["Content"] = tmsg[10]
        obj["Message"] = tmsg[7]
        return True, TargetIP
    else: 
        return False, "" 

def analyzeEvent(msg):
    if msg.find("Traps Agent") != -1:
        if (msg.find("Prevention Event")!=-1 and msg.find("Threat")!=-1):
            obj = {}
            result, TargetIP = eventToObj(msg, obj)
            if result: 
                result, resp = fs.postCDEX(fs.DEXAuth, TargetIP, propertyName, obj)
                if LOG_ENABLE:
                    logging.info("%s: %s" %(result, resp)) 

class SyslogUDPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = bytes.decode(self.request[0].strip())
        socket = self.request[1]
        print( "%s : " % self.client_address[0], str(data))
        threading.Thread(target=analyzeEvent, args=(str(data),)).start()
        if LOG_ENABLE:
            
            logging.info(str(data))

if __name__ == "__main__":
    
    try:
        server = SocketServer.UDPServer((HOST,PORT), SyslogUDPHandler)
        print("Running Syslog UDP Server at: %s, port %s" %(HOST, PORT))
        server.serve_forever(poll_interval=0.5)
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print ("Crtl+C Pressed. Shutting down.")
