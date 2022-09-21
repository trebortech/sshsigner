import optparse
import ssl

# 3rd party modules
import tornado.ioloop
import tornado.web


import application.signer as SIGNER
import application.utils as UTILS

'''
Before running this setup

1. Install / Configure wireguard vpn
2. Install / Configure hsm connector (HSM must be listening on port 1111)
3. Add / Authorize hsm to management server


hsm @ 127.0.0.1:1111

hsm should be configured to listen on 172.16.0.0 and 127.0.0.1


'''


def parse_options():
    usage = """\
    rpi_image_grabber.py [options...]
    This script will startup the image grabber service."""
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-i", "--hsmipport", dest="hsmipport", default='', help="IP:Port for the YubiHSM",)
    parser.add_option("-u", "--userid", dest="userid", default='', help="What userid for the YubiHSM",)
    parser.add_option("-p", "--userpass", dest="userpass", default='', help="Password for the YubiHSM user",)
    parser.add_option("-w", "--wrapid", dest="wrapid", default='', help="Wrap ID on the YubiHSM",)
    parser.add_option("-b", "--bucketname", dest="bucketname", default='', help="Bucket name in AWS",)
    parser.add_option("-l", "--localpath", dest="localpath", default='', help="Local path to store files",)
    parser.add_option("-f", "--filename", dest="filename", default='', help="File to download",)

    options, _ = parser.parse_args()
    # All options are required
    return options


'''
# Before start checks
- hsmnet configured
- hsm inserted


# Setup
DONE - Create certificate for SSL
DONE - Create certificate for TimeServer (aka Signer Cert)

DONE - Post TimeServer public cert
DONE - Note to upload that cert to mgmt server before continuing

# Running
- Login of user HSM Pin 

After Login

- List of Templates to choose 
- Box for user certificate to sign 

Submit

- Return Public to download 
'''


class DefaultHandler(tornado.web.RequestHandler):
    """
    Default handler for 404
    """

    def prepare(self):
        self.set_status(404)
        self.render("error/404.html")


def ssl_ctx():

    sitecert, sitekey, message = UTILS.createcert("server-ssl")
    print(message)
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(sitecert, sitekey)
    return ssl_ctx


def app(options):
    settings = {
        "login_url": "/",
        "debug": True,
        "default_handler_class": DefaultHandler,
        "template_path": "./application/templates",
        "static_path": "./application/static",
    }

    handlers = [
        (r"/setup", SIGNER.SetupHandler),
        (r"/sshsigner", SIGNER.Signer)
        ]

    application = tornado.web.Application(handlers, **settings)
    http_server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_ctx())
    http_server.listen(443)
    tornado.ioloop.IOLoop.instance().start()




if __name__ == "__main__":
    options = parse_options()
    app(options)