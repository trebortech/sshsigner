
import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

import ssh_requests



def req():

    ssh_key = """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCZjvFRgbB+WdBMpVsyY5jN6bFfs0YwkPHSLWweb3IAJAHAfibTX4JdmAOVMO3Kj8BRpMKoN6uNF/vEpItAKbcxkTjXPByaT30JrM5GhjL/96nBIJ6lzxe+86T0PGdD9O5c0StXy6HT08NlD+ROkV/ecGIHBWczvUxPomf1F6k6wtn3HCLav6EY+rmUfSQQh3ckqT/c52WQan9EE9JlgyvVw73td88+sR8KE562xVv/LJQZzzBr8TXcUusgyBuLm096Oq4XAgzayXr53vwAIoYoYd3wChOk26bTJn1KTMdiJ3oN1+2t3BJD3ixoJWHoVMKu2Tb4ig/hRiwXUcre0sdm1z3drxueit5/fZnxRZ+cFQffhozxoCYH7N47TSXvJl+DEgnJ9IaR9ksu68L5ZcdKFJ8b1WQz9N64FrBYlo5TPutBHj/CZG4kJ5qctUvR9oEFgNIA3lbefpDwV8+Msc2sCdqROBsUyN/36BIAk3xZ0GF3vIsskotVVcASd2m6GFU= Key for rsync user"""
    
    ca_key = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAzO7oiij6u7hnJN5p7pkx
ly1k7dNVRkw9HuLegiqwKt6mHrG/xKXcQrga/Q/7OWV/9i8iz3XtGX3w8PL7+t4p
mW6SlBK8weAFFQXCQpqNAvcYRHdAM3fGY2joDOwwjU+3/e264GaAQFbiMo4DUuwi
t/tCr2oQKNhhdUR70zVhbbaXTPcoxLnOZDBx1pcNAqTJdmARjD8auAZDJkRMRftx
ZKOZyDJO6zp4st3XmrPDfkm/7wJ76Z954p7CRYZPeMQ8stSdfwAGPUhcEHbwuX4C
NqKssWSBC3vFeO07yozljFMiwcNM6mHqFLyGKCms+jOYx7+Mo9o8hLfnBDQUbcRv
e4KTeDWtenYWV77YPSifjhEPkcEonkT6clz1IRoAlu787MlieVJSj413/1JNAAtg
c7SJVRQN4ExKU7HRh/DtmdEr3nsRqzFgSerbBGghMK1eVPouln7rRViODsYxhwjY
TgOnzX3dgC0ofK9MQdITZJD6ScusUBLhvrT/jf5oznrXvDG8xZAD3SQKbSEJeIjd
uhSXPNvLQScLwjByyPWy2BMx1DPs9viORbmwFDhxzYOZE7QOkG/aJM0XfydinjTL
IWzQ36mCQPcExjadCNDUOU0ZJrkubW7niZZEx55Qkth+IabL3xasSLB2khQucJwC
+1he/AQZDPcesDBpfIaxFz0CAwEAAQ==
-----END PUBLIC KEY-----""".encode()

    ca_public_key = serialization.load_pem_public_key(ca_key, backend=default_backend())
    ssh_public_key = serialization.load_ssh_public_key(ssh_key, backend=default_backend())

    identity = "user-identity"
    option = ""
    principals = "rbooth"

    now = int(time.time())
    oneyear = 31536000
    nb = now - 60
    na = now + oneyear

    serial = int(time.time())
    req = ssh_requests.create_request(
        ca_public_key,
        ssh_public_key,
        identity,
        principals,
        option,
        nb,
        na,
        serial
    )
    import pdb;pdb.set_trace()
    

if __name__ == "__main__":
    ret()
