import subprocess
import socket
import re
import os
import time
import struct

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, utils
from cryptography.hazmat.primitives import serialization
from binascii import b2a_hex

from yubihsm import YubiHsm
from yubihsm.objects import AsymmetricKey

import sshsigner.ssh_requests as ssh_requests



def _run(cmd, mydata=""):
    """
    The run function is used to execute cli commands. It can be utilized
    interactively with stdin being passed in via the mydata value.
    cmd is a python list that will be pulled together to form a single line to
    execute.
    """
    try:
        ret = subprocess.run(
            cmd,
            capture_output=True,
            timeout=60,
            text=True,
            check=True,
            shell=False,
            input=mydata,
        )
        return ret
    except Exception as err:
        print(f"Error running {cmd}")


def createcert(name, datadir):
    path = f"{datadir}/ssl/{name}"
    hostname = socket.gethostname()

    # Check if certs already exist
    certcreated = os.path.exists(f"{path}.key")

    if certcreated:
        message = f"{path}.key already exists. Moving on."
    else:    
        createcert = (
            "openssl  req  -new  -newkey  rsa:2048  -days  365  -nodes  "
            f"-subj  /C=US/ST=Texas/L=Round Rock/O=TreborTech, LLc/OU=Labs/CN={hostname}  "
            f"-addext  subjectAltName=DNS:{hostname}  "
            "-addext  keyUsage=digitalSignature,keyEncipherment  "
            "-addext  extendedKeyUsage=serverAuth,clientAuth  "
            f"-x509  -keyout  {path}.key  -out  {path}.crt  -pubkey"
        )

        createcert = re.split(" {2,}", createcert)

        _run(createcert)
        message = f"Created new certs {path}.crt"

    return (f"{path}.crt", f"{path}.key", message)


def hsm_session(port, userid, userpass):
    hsm = YubiHsm.connect(f"http://127.0.0.1:{port}")
    session = hsm.create_session_derived(int(userid), userpass)
    return session


def req(sshkey, hsmsession, ca_id, principals, host_tz_priv_key):

    cakey = get_pub_key(hsmsession, ca_id)

    ca_public_key = serialization.load_pem_public_key(cakey, backend=default_backend())
    ssh_public_key = serialization.load_ssh_public_key(sshkey, backend=default_backend())
    host_tz_key = serialization.load_pem_private_key(host_tz_priv_key, password=None, backend=default_backend())

    identity = "user-identity"
    option = ""
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

    # Hash the request
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(req)
    request_hash = digest.finalize()

    # Hash request + timestamp for signing
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(request_hash)
    digest.update(struct.pack('!I', now))
    message_hash = digest.finalize()

    signature = host_tz_key.sign(
            message_hash,
            padding.PKCS1v15(),
            utils.Prehashed(hashes.SHA256())
    )

    with open('req.dat', 'wb') as f:
        f.write(struct.pack('!I', now) + signature + req)


def sign_req(hsmsession, ca_id, template_id, request):
    ca = AsymmetricKey(hsmsession, ca_id)
    sshcert = ca.sign_ssh_certificate(template_id, request)
    return sshcert


def get_pub_key(hsmsession, keyid):
    asymmkey = AsymmetricKey(hsmsession, keyid)
    public_key = asymmkey.get_public_key()
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()

    return pem


def get_hsm_list(portfile):
    
    try:
        lsusb_cmd = "lsusb  -d  1050:0030  -v"
        lsusb = re.split(" {2,}", lsusb_cmd)
        hsmlist = _run(lsusb)
        hsmlist_arr = hsmlist.stdout.split("\n")

        serialport = {}

        with open(portfile, 'r') as file:
            for _ in range(1):
                next(file)
            for line in file:
                serial, port = line.split(":")
                serialport[int(serial)] = int(port)

        connected_hsms = {}
        for lineitem in hsmlist_arr:
            if lineitem.lstrip()[:7] == "iSerial":
                serialnumber = int(lineitem[-10:])
                connected_hsms[str(serialnumber)] = str(serialport[serialnumber])
    except Exception as err:
        connected_hsms = {"Nothing found": "000000"}
    
    return connected_hsms


def get_templates(hsmsession):

    objtemplates = hsmsession.list_objects(object_type = 6)

    templates = {}
    for obj in objtemplates:
        det = obj.get_info()

        templateid = det.id
        templatelabel = det.label
        templates[str(templateid)] = templatelabel

    return templates