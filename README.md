# SSH Signer

## Summary

The goal of this applicaiton is to make an easy to deploy CA Signed SSH key environment. Restricting the signing auhtority to key organization individuals aka Key Custodians.
By using the YubiHSM as the backbone of this architecture you not only have a more secure storage facility but also visibility to who is signing and when they are signing ssh keys.

***

## Install

** Requirements **
- yubihsm-connector
- Linux OS
- root install [^root] 

***
*NOTE: You need to update tag version*

https://github.com/trebortech/sshsigner/tags

```
pip3 install https://github.com/trebortech/sshsigner/archive/refs/tags/YY.MM.DD.BB.tar.gz
```
Please update with the correct tag version you want to pull

Once installed
```
tt-sshsigner
```

-d = data directory. Defaults to /opt/sshsigner


#### My Random Notes

- UDEV script (yubihsm.rules) will trigger the SystemD service (yubihsm-start.service). SystemD service will execute the hsminsert.sh script.

<details><summary>On YubiHSM insert</summary>

```mermaid

%%{init: {
  'theme':'base',
  'themeVariables': {
      'tertiaryColor': '#cccccc',
      'mainBkg': '#e3dada',
      'actorTextColor': '#b1b1b5',
      'actorBkg': '#0c8796',
      'signalColor': '#0c8796',
      'signalTextColor': '#b1b1b5',
      'sequenceNumberColor': '#b1b1b5'
      }
    }
  }%%


sequenceDiagram
  autonumber
  participant HSM
  participant UDEV
  Note over UDEV: /etc/udev/rules.d/yubihsm.rules
  participant SystemD
  Note over SystemD: /etc/systemd/system/yubihsm-start.service
  participant Script
  Note over Script: /usr/local/bin/hsminsert.sh

  HSM->>UDEV: Inserted
  UDEV->>SystemD: YubiHSM was inserted  
  SystemD->>Script: Run Script
  Script->>Script: Start service for inserted YubiHSM

```

</details>

- My test RPi has an oled screen. The IP address will show of the device. Script located at application/xscripts/oled.py


## RUN

```bash
python3 app_signer.py
```


### TODO

- [X] Installation README with requirements
- [X] Installation scripts
- [X] UDEV script to configure YubiHSM on insert
- [X] Create "timestamp" cert
- [X] Create Login Page
- [X] Create Sign Key page
- [ ] Create walk through video
- [ ] Create systemd script for oled and app
- [X] Update this README file



[^root]: lsusb requires root access. Also, we are bonding to port 443 but we should be able to work around that. I'm still working on least priv user.