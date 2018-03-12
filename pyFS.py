#!/usr/bin/env python
import os
import sys

import yaml
import json
import requests 
import datetime as dt 

import shutil
from requests.auth import HTTPBasicAuth

class pyFS(object):
    """ForeScout WebAPI wrapper Class:

    Attributes:
        user: UserName used to access ForeScout webAPIs.
        password: Password used to access ForeScout webAPIs.
        host: ForeScout CounterACT Appliance IP (such as 10.0.2.100) 

    """

    def __init__(self, fsConfigFile = 'fsconfig.yml'):
        """Initializes pyFS object with ip and credentials provided for both web-api and DEX web-services."""
        stream = open(fsConfigFile, "r")
        docs = yaml.load_all(stream)
        for doc in docs:
            for k,v in doc.items():
                if k.find('counterActIP')!=-1:
                    self.counterAct = v
                if k.find('Web-API')!=-1:
                    self.user= v['User']
                    self.password= v['Password']
                if k.find('DEX')!= -1:
                    self.DEXuser= v['User']
                    self.DEXpassword= v['Password']
                    self.DEXAuth= HTTPBasicAuth(self.DEXuser, self.DEXpassword)
        stream.close() 
        
        self.cacheLogin = dt.timedelta(minutes=5)
        self.cacheTime1 = dt.timedelta(hours=1)
        self.cacheTime2 = dt.timedelta(hours=24)
        
        self.endpoints = {}
        self.hosts = []
        
        self.baseAPI = 'https://%s/api'% self.counterAct 
        self.loginURL = '%s/login'% self.baseAPI
        self.loggedin = False 
        #self.login()
        
        
    def userpass(self, user, password, counteractip):
        """Returns pyFS object with credentials provided and auto-generating base webAPI."""
        self.user = user
        self.password = password 
        self.counterAct = counteractip
        
        self.cacheLogin = dt.timedelta(minutes=5)
        self.cacheTime1 = dt.timedelta(hours=1)
        self.cacheTime2 = dt.timedelta(hours=24)
        
        self.endpoints = {}
        self.hosts = []
        
        self.baseAPI = 'https://%s/api'% self.counterAct 
        self.loginURL = '%s/login'% self.baseAPI
        self.loggedin = False 
        self.login()
        return self 
    
    def initDEX(self, user, password): 
        """Initializes a DEX Username / Password and returns Authorization Code to be used in postDEX."""
        self.DEXuser = user 
        self.DEXpassword = password
        return HTTPBasicAuth(user, password)
    
    def postDEX(self, auth, epip, _property, _value): 
        """Posts via auth (result of initDEX) to CounterACT for Endpoint IP: epip, using property: _property and value: _value."""
        postURL = "https://%s/fsapi/niCore/Hosts" % self.counterAct
        headers = {'Content-Type': 'application/xml', 'Accept': 'application/xml'}
        post_data = """<?xml version='1.0' encoding='utf-8'?>
        <FSAPI TYPE="request" API_VERSION="1.0">
          <TRANSACTION TYPE="update">
            <OPTIONS CREATE_NEW_HOST="true"/>
            <HOST_KEY NAME="ip" VALUE="%s"/>
            <PROPERTIES>
              <PROPERTY NAME="%s">
                <VALUE>%s</VALUE>
              </PROPERTY>
            </PROPERTIES>
          </TRANSACTION>
        </FSAPI>
        """ %(epip, _property, _value)
        r = requests.post(postURL, headers=headers,auth=auth, data=post_data, verify=False)
        return r.status_code == 200, r.content.decode('utf-8')

    def postCDEX(self, auth, epip, _property, _Obj): 
        """Posts via auth (result of initDEX) to CounterACT for Endpoint IP: epip, using Composite property: _property and object: _Obj"""
        postURL = "https://%s/fsapi/niCore/Hosts" % self.counterAct
        headers = {'Content-Type': 'application/xml', 'Accept': 'application/xml'}
        post_data_header = """<?xml version='1.0' encoding='utf-8'?>
        <FSAPI TYPE="request" API_VERSION="1.0">
          <TRANSACTION TYPE="update">
            <OPTIONS CREATE_NEW_HOST="true"/>
            <HOST_KEY NAME="ip" VALUE="%s"/>
            <PROPERTIES>
              <TABLE_PROPERTY NAME="%s">
                <ROW>
        """ %(epip, _property)
        
        post_data_footer = """
                  </ROW>
                </TABLE_PROPERTY> 
            </PROPERTIES>
          </TRANSACTION>
        </FSAPI>
        """

        post_data_cprop = ""; 
        for k,v in _Obj.items(): 
            post_data_cprop += """
                    <CPROPERTY NAME="%s"> 
                        <CVALUE>%s</CVALUE>
                    </CPROPERTY> 
                 
            """ %(k, v)

        post_data = post_data_header + post_data_cprop + post_data_footer
        r = requests.post(postURL, headers=headers,auth=auth, data=post_data, verify=False)
        return r.status_code == 200, r.content.decode('utf-8')
    
    def deleteDEX(self, auth, epip, _property): 
        """Deletes via auth (result of initDEX) to CounterACT for Endpoint IP: epip, using property: _property"""
        postURL = "https://%s/fsapi/niCore/Hosts" % self.counterAct
        headers = {'Content-Type': 'application/xml', 'Accept': 'application/xml'}
        endpointip = '10.0.2.51'
        post_data = """<?xml version='1.0' encoding='utf-8'?>
        <FSAPI TYPE="request" API_VERSION="1.0">
            <TRANSACTION TYPE="delete">
                <HOST_KEY NAME="ip" VALUE="%s"/>
                <PROPERTIES>
                    <PROPERTY NAME="%s" />
                </PROPERTIES>
            </TRANSACTION>
        </FSAPI>
        """ %(epip, _property)
        r = requests.post(postURL, headers=headers,auth=auth, data=post_data, verify=False)
        return r.status_code == 200, r.content.decode('utf-8')
         
    def login(self):
        """Login to CounterACT - check if token time > self.cacheLogin(5mins) to relogin automatically."""
        if self.loggedin: 
            if (dt.datetime.now() - self.lastLogin) > self.cacheLogin:        
                r = requests.post(self.loginURL, {"username": self.user, "password": self.password}, verify=False)
                if r.status_code == 200: 
                    auth = r.content
                    self.headers = {'Authorization': auth}
                    self.lastLogin = dt.datetime.now()
                    self.loggedin = True 
                    return True
                else:
                    # Error while logging in 
                    self.loggedin = False
                    return False 
            else: 
                return True 
        else: 
            r = requests.post(self.loginURL, {"username": self.user, "password": self.password}, verify=False)
            if r.status_code == 200: 
                auth = r.content
                self.headers = {'Authorization': auth}
                self.lastLogin = dt.datetime.now()
                self.loggedin = True 
                return True
            else:
                # Error while logging in
                self.loggedin = False
                return False
    
    def getAllHostsFields(self): 
        """Retrieves list of hostfields from CounterACT webAPI."""
        if self.login(): 
            req = '%s/hostfields'% self.baseAPI
            resp = requests.get(req, headers=self.headers, verify=False)
            if resp.status_code == 200: 
                jresp = json.loads(resp.content.decode('utf-8'))
                self.hostfields = jresp[u'hostFields']
                self.hostfieldsTimeStamp = dt.datetime.now()
                return True 
            else: 
                return False 
        else: 
            return False 
        
    def checkHostField(self, hf):
        """Verifies if hf exists in HostFields extracted from CounterACT"""
        if self.getAllHostsFields():
            for field in self.hostfields:
                if hf == str(field[u'name']):
                    return True 
        return False 
    
    def getHostFieldName(self, hf): 
        for hostfield in self.hostfields:
            if hostfield[u'name'].find(hf) != -1: 
                return hostfield[u'name']
        return None 
    
    def getHostFieldsNames(self, hf): 
        resp = [] 
        for hostfield in self.hostfields:
            if hostfield[u'name'].find(hf) != -1: 
                resp.append(hostfield[u'name'])
        return resp 
    
    def getEndPointFieldsNames(self, dev): 
        """Extract Availalbe Properties for a specific endpoint."""
        return dev[u'fields'].keys()
    
    def getEndPointFieldValue(self, dev, fieldName):
        if type(dev[u'fields'][fieldName]) != type([]):
            return dev[u'fields'][fieldName]['value'] 
        else: 
            resp = '[ ' 
            i = 0
            for v in dev[u'fields'][fieldName]:
                resp += v['value']
                if i<(len(dev[u'fields'][fieldName])-1): 
                    resp += ', '
                i+=1
            resp += ' ]'
            return resp 
    
    def getEndPointFieldValueRaw(self, dev, fieldName):
        if type(dev[u'fields'][fieldName]) != type([]):
            return dev[u'fields'][fieldName]['value'] 
        else:
            return dev[u'fields'][fieldName]
        
    def gethosts(self): 
        """Retrieves list of active hosts from CounterACT webAPI."""
        if self.login(): 
            req = '%s/hosts'% self.baseAPI
            resp = requests.get(req, headers=self.headers, verify=False)
            if resp.status_code == 200: 
                #print(resp.content)
                jresp = json.loads(resp.content.decode('utf-8'))
                self.hosts = jresp[u'hosts']
                self.hostsTimeStamp = dt.datetime.now()
                return True 
            else: 
                return False 
        else: 
            return False 
    
    def gethostsByProp(self, prop, val): 
        """Retrieves list of hosts with prop value equal to val from CounterACT webAPI."""
        if self.login(): 
            if self.checkHostField(prop):     
                req = '%s/hosts?%s=%s'% (self.baseAPI, prop, val)
                resp = requests.get(req, headers=self.headers, verify=False)
                if resp.status_code == 200: 
                    #print(resp.content)
                    jresp = json.loads(resp.content.decode('utf-8'))
                    return  jresp[u'hosts']
                else: 
                    return False
            else:
                return False
        else: 
            return False 
        
    def gethostsByRules(self, rulesList): 
        """Retrieves list of hosts matching ruleIDs from CounterACT webAPI."""
        if self.login(): 
            req = '%s/hosts'% self.baseAPI
            req +='?matchRuleId=%s' %rulesList[0]
            if len(rulesList)>1: 
                for ruleId in rulesList[1:len(rulesList)]:
                    req +=',%s' % ruleId
                return req
            
            resp = requests.get(req, headers=self.headers, verify=False)
            if resp.status_code == 200: 
                jresp = json.loads(resp.content.decode('utf-8'))
                return jresp[u'hosts'] 
            else: 
                return None 
        else: 
            return None
        
    def getpolicies(self): 
        """Retrieves list of policies from CounterACT webAPI."""
        if self.login(): 
            req = '%s/policies'% self.baseAPI
            resp = requests.get(req, headers=self.headers, verify=False)
            if resp.status_code == 200: 
                jresp = json.loads(resp.content.decode('utf-8'))
                self.policies = jresp[u'policies']
                self.policiesTimeStamp = dt.datetime.now()
                return True 
            else: 
                return False 
        else: 
            return False
    
    def getPolicyId(self, policyName):
        for pol in self.policies: 
            if pol[u'name'].find(policyName)!= -1: 
                return pol[u'policyId']
        return None
    
    def getRules(self, policyID):
        for pol in self.policies: 
            if pol[u'policyId'] == policyID: 
                return pol[u'rules']
        return None
    
    def getRuleId(self, ruleName, policyRules):
        for rule in policyRules:
            if rule[u'name'].find(ruleName) != -1: 
                return rule[u'ruleId']
        return None

    def gethostIDbyIP(self, hostip):
        """Retrieves hostID from CounterACT webAPI based on host IP."""
        if self.hosts == []: 
            return None 
        for host in self.hosts: 
            if host[u'ip'] == hostip: # Enhancement: convert to normalized IP in future
                return host[u'hostId']
        return None 
    
    def gethostIDbyMAC(self, hostmac):
        """Retrieves hostID from CounterACT webAPI based on host MAC Address."""
        if self.hosts == []: 
            return None 
        for host in self.hosts: 
            if host[u'mac'] == hostmac: # Enhancement: convert to normalized MAC in future 
                return host[u'hostId']
        return None 
        
    def gethostByID(self, hostid): 
        """Retrieves host properties from CounterACT webAPI by hostID."""
        if self.login(): 
            req = '%s/hosts/%s'% (self.baseAPI, hostid)
            resp = requests.get(req, headers=self.headers, verify=False)
            if resp.status_code == 200: 
                jresp = json.loads(resp.content.decode('utf-8'))
                #self.hostsTimeStamp = dt.datetime.now()
                return True, jresp[u'host']
            else: 
                return False, None  
        else: 
            return False, None  
    
    def DEXAuth(self):
        return self.DEXAuth