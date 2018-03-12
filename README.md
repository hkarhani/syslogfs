# syslogfs 

This is lightweight Tiny UDP Syslog Server which can be configured:
  1. To receive UDP Syslogs from PAN Traps ESM Server - currently configured for Treats - Threat Prevention Messages. 
  2. Send DEX Updates to ForeScout CounterACT   

There are couple of Settings that need to be configured before running the Script: 

## 1. Configure Data Exchange DEX Extended Module on CounterACT:

```
     a. To Accept requests from Host IP running the Script
     b. Configure a new DEX Account (note Name@Username to be used in below configuration)
     b. To Define a Web-Services Composite Property (default name is "TrapsEvents"). 
        i. You need to create a Web-Service Property in your ForeScout CounterACT / Data-Exchange DEX / Web-Services Properties 
           Property Name: default "TrapsEvents" - Type Composite (configurable from syslogfs.py)
        ii. Then Configure the following mapped sub-properties: 
			- TimeStamp (String) - Inv 
			- Source (String) - Inv 
			- Type (String) - Inv 
			- Content (String) - Inv 
			- Message (String) 
```

Note: For DEX-Web-Services Account make sure to note both Account name / username as they need to be entered as: name@username in the following section. 

## 2. Edit fsconfig.yaml file: 

Fill in the IP, User/Pass for Web-APIs and User/Pass for DEX-Web-Services Account: 

```
---
counterActIP:  
Web-API: 
    User: 
    Password:  
DEX-Web-Serivces: 
    User: 
    Password:  
```
## 3. Edit any customized settings in the user data header of "syslogfs.py":

 ```
LOG_ENABLE = False          # Set to True if you want to enable Logging to LOG_FILE - Screen Logging is enabled by default.  
LOG_FILE = 'logfile.log'    # filename of Logging File 
HOST, PORT = "0.0.0.0", 514 # IP (0.0.0.0 : for all interfaces), UDP port setting (default UDP Port= 514)

propertyName = "TrapsEvents" # Property name to be used in FS Web-Service DEX Composite Property 

```

## 4. Run the Script on the host (make sure UDP port in not in use - default is UDP port 514):

```
 python syslogfs.py 

 OR

 sudo python syslogfs.py 
```
