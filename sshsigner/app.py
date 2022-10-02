'''
This is the main launching point for the client SSH Signer webpage
'''
import optparse
import ssl
import os
import sys

currdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(currdir)

# 3rd party modules
import tornado.ioloop
import tornado.web

import signer as SIGNER
import utils as UTILS

#currpath = os.path.realpath(__file__)[:- len(os.path.basename(__file__))]

def parse_options():
    usage = """\
    app_signer.py [options...]
    This script will startup the SSH Signer service."""
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-d", "--datadir", dest="datadir", default='/opt/sshsigner', help="Storage directory",)

    options, _ = parser.parse_args()
    # All options are required
    return options


class DefaultHandler(tornado.web.RequestHandler):
    """
    Default handler for 404
    """
    def prepare(self):
        self.set_status(404)
        self.render("404.html")


def ssl_ctx(datadir):

    sitecert, sitekey, message = UTILS.createcert("server-ssl", datadir)
    print(message)
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(sitecert, sitekey)
    return ssl_ctx


def app(options):

    # Create data directory

    if os.path.exists(options.datadir):
        print("Data directory already exists")
    else:
        os.mkdir(options.datadir)

    settings = {
        "login_url": "/",
        "debug": True,
        "default_handler_class": DefaultHandler,
        "template_path": f"{currdir}/templates",
        "static_path": f"{currdir}/static",
        "datadir": options.datadir,
    }

    handlers = [
        (r"/", SIGNER.DefaultHandler),
        (r"/v1/data", SIGNER.DataHandler),
        (r"/setup", SIGNER.SetupHandler),
        (r"/sshsigner", SIGNER.SignerHandler)
        ]

    application = tornado.web.Application(handlers, **settings)
    http_server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_ctx(options.datadir))
    http_server.listen(443)
    tornado.ioloop.IOLoop.instance().start()

def main():
    options = parse_options()
    app(options)

if __name__ == "__main__":
    main()