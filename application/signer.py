import re

import tornado.web

import application.utils as UTILS


class SetupHandler(tornado.web.RequestHandler):

    def get(self):
        timecert, timekey, message = UTILS.createcert("timestamp")
        timecertfile = open(timecert, "r").read()
        pubkey = re.split("((-----BEGIN PUBLIC KEY-----)(.|\n)*(-----END PUBLIC KEY-----))", timecertfile)
        self.render("setup.html", timeservercert=pubkey[1])


class SignerHandler(tornado.web.RequestHandler):

