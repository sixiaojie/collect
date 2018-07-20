#!/usr/bin/env python
#coding:utf8
import urllib2
import json,sys,os
import param
import MySQLdb
import datetime
import time

class ZabbixApi(object):
    def __init__(self,username="sijie",password="sijie",server="http://127.0.0.1/api_jsonrpc.php",host_list='/etc/work_server_config',db_host="",db_username="",db_password=""):
        self.username = username
        self.password = password
        self.server = server
        self.list = host_list
        self.db_host = db_host
        self.db_username = db_username
        self.db_passwprd = db_password
        self.log = self.log()
        self.header = {"Content-Type": "application/json"}
        self.token = self.login_token()
	self.cursor = self.db()

    def _reponse(self,data):
        request = urllib2.Request(self.server,data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except urllib2.URLError as e:
            print "Failed, Please Check :", e.code
            sys.exit(10)
        return result

    def log(self):
        f = open("./action.log","a+")
        return f

    def logger(self,msg):
        nowTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log.write("%s: %s\n" %(nowTime,msg))

    def login_token(self):
        data = json.dumps(param.param['user']['login']) %(self.username,self.password)
        result =self._reponse(data)
        response = json.loads(result.read())
        result.close()
        return response['result']


    def db(self):
        self.db = MySQLdb.connect(host=self.db_host,user=self.db_username,passwd=self.db_passwprd,charset="utf8")
        cursor = self.db.cursor()
	return cursor

    def get_all_host(self):
	param.param['host']['get']['auth'] = self.token
	data = param.param['host']['get']
	result = self._reponse(json.dumps(data))
	for item in json.loads(result.read())['result']:
		self.cursor.execute("insert into collect.host values(%s,'%s')" %(item['hostid'],item['host']))
		self.db.commit()
		for group in item['groups']:
			self.cursor.execute("insert into collect.relation values('%s','%s')" %(item['hostid'],group["groupid"]))
			self.db.commit()

    def get_all_group(self):
	param.param["group"]['get']['auth'] = self.token	
	data = param.param['group']['get']
        result = self._reponse(json.dumps(data))
        for group in  json.loads(result.read())['result']:
		self.cursor.execute("insert into collect.groups values(%s,'%s')" %(group["groupid"],group["name"]))
		self.db.commit()

    def pull_item_data(self):
	now= int(time.time())
	before = 1532080000
	param.param["history"]["get"]["params"]["time_from"]=before
	param.param["history"]["get"]["params"]["time_till"]=now
	param.param['history']['get']['auth'] = self.token
	param.param['history']['get']['params']['hostids'] = "10105"
	data =  param.param["history"]["get"]
	result = self._reponse(json.dumps(data))
	print result.read()
	print json.loads(result.read())['result']
		

    def _close(self):
	self.cursor.close()
	self.db.close()
	self.log.close()

if __name__ == "__main__":
    zabbix = ZabbixApi(server="https://monitor.kuainiujinke.com/api_jsonrpc.php",db_username="sijie",db_password="sijie",db_host="127.0.0.1")
    zabbix.pull_item_data()
