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
2. Add / Authorize hsm to management server
'''


def parse_options():
    usage = """\
    app_signer.py [options...]
    This script will startup the SSH Signer service."""
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-i", "--hsmipport", dest="hsmipport", default='', help="IP:Port for the YubiHSM",)

    options, _ = parser.parse_args()
    # All options are required
    return options


'''
# Before start checks
- hsmnet configured
- hsm inserted


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
        (r"/", SIGNER.DefaultHandler),
        (r"/v1/data", SIGNER.DataHandler),
        (r"/setup", SIGNER.SetupHandler),
        (r"/sshsigner", SIGNER.SignerHandler)
        ]

    application = tornado.web.Application(handlers, **settings)
    http_server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_ctx())
    http_server.listen(443)
    tornado.ioloop.IOLoop.instance().start()




if __name__ == "__main__":
    options = parse_options()
    app(options)