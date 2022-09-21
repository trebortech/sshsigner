import time
import os
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306



i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
disp.fill(0)
disp.show()

width = disp.width
height = disp.height
image = Image.new("1", (width, height))

draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, width, height), outline=0, fill=0)

padding = -1
top = padding
bottom = height - padding
x = 0

font = ImageFont.truetype('/home/rbooth/Essential.ttf', 21)
customfont = ImageFont.truetype('/home/rbooth/custom.ttf', 21)
nextpage = 1

while True:
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    cmd = "hostname -I | cut -d' ' -f1"
    IP = subprocess.check_output(cmd, shell=True).decode("utf-8")

    if nextpage == 1:
        nextpage = 2
        draw.text((x, top), "HTTPS://", font=font, fill=255)
        draw.text((x, top + 15), IP, font=font, fill=255)

    elif nextpage == 2:
        hcmicon = "a"
        showme = "SSH KEY SIGNER"
        if os.path.exists("notify.txt"):
            nextpage = 3
        else:
            nextpage = 1
        draw.text((x, top + 8), hcmicon, font=customfont, fill=255)
        draw.text((x + 30, top + 8), showme, font=font, fill=255)

    elif nextpage == 3:
        notifyme = open("notify.txt", "r").read()
        draw.text((x, top + 8), notifyme, font=font, fill=255)
        nextpage=1


    disp.image(image)
    disp.show()
    time.sleep(5)
