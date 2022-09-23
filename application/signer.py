import re
import socket
import json
import os
import shutil

import tornado.web

import application.utils as UTILS

PORTFILE="/usr/local/bin/ports.conf"

class DefaultHandler(tornado.web.RequestHandler):

    def get(self):

        path = f"./application/ssl/timestamp"
        
        if os.path.exists(f"{path}.key"):
            self.redirect("/sshsigner")
        else:
            self.redirect("/setup")


class SetupHandler(tornado.web.RequestHandler):

    def get(self):

        '''
        Deploy out scripts to handle auto configure of YubiHSM on insert
        '''

        if os.path.exists("/etc/udev/rules.d/yubihsm.rules"):
            print("udev rule already in place")
        else:
            shutil.copy('./application/xscripts/yubihsm.rules', '/etc/udev/rules.d/yubihsm.rules')
        
        if os.path.exists("/etc/systemd/system/yubihsm-start.service"):
            print("SystemD rule already in place")
        else:
            shutil.copy('./application/xscripts/yubihsm-start.service', '/etc/systemd/system/yubihsm-start.service')
            os.chmod('/etc/systemd/system/yubihsm-start.service', 360)

        if os.path.exists("/usr/local/bin/hsminsert.sh"):
            print("hsminsert already deployed")
        else:
            shutil.copy('./application/xscripts/hsminsert.sh', '/usr/local/bin/hsminsert.sh')
            os.chmod('/usr/local/bin/hsminsert.sh', 360)

        hostname = socket.gethostname()
        # Creaet a timestamp cert if it doesn't already exist
        timecert, timekey, message = UTILS.createcert("timestamp")
        timecertfile = open(timecert, "r").read()
        pubkey = re.split("((-----BEGIN PUBLIC KEY-----)(.|\n)*(-----END PUBLIC KEY-----))", timecertfile)

        self.render("setup.html", hostname=hostname, timeservercert=pubkey[1])


class SignerHandler(tornado.web.RequestHandler):

    def get(self):
        hostname = socket.gethostname()

        self.render("app.html", hostname=hostname)


    def post(self):
        payload = json.loads(self.request.body)
        ret = []
        userid = payload.get("userid", "")
        usercode = payload.get("usercode", "")
        hsmport = payload.get("hsmport", "")
        
        template_id, template_label, ca_id = payload.get("templateid", "").split("-")
        principals = payload.get("principals", "")
        ssh_key = payload.get("sshkey", "")
       
        host_tx_priv_key = open("./application/ssl/timestamp.key", "rb").read()
        
        hsmsession = UTILS.hsm_session(hsmport, userid, usercode)
        
        req = UTILS.req(ssh_key, hsmsession, ca_id, principals, host_tx_priv_key)
        ret = UTILS.sign_req(hsmsession, ca_id, template_id, req)

        self.write(str(ret))


class DataHandler(tornado.web.RequestHandler):
    
    def post(self):
        payload = json.loads(self.request.body)
        method = payload.get("method", "")

        ret = []
        if method == "get_yubihsm_list":
            '''
            Return a list of plugged in YubiHSM
            '''
            ret = UTILS.get_hsm_list(PORTFILE)

        elif method == "get_ssh_templates":

            hsmport = payload.get("hsmport", "")
            userid = payload.get("userid", "")
            usercode = payload.get("usercode", "")

            hsmsession = UTILS.hsm_session(hsmport, userid, usercode)
            ret = UTILS.get_templates(hsmsession)
        
        self.write(str(ret))



