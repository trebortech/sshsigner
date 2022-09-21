import subprocess
import socket
import re
import os


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


def createcert(name):
    path = f"./application/ssl/{name}"
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