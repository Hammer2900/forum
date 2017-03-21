# -*- coding: utf-8 -*-
from os.path import expanduser
import os
import markdown
import requests


def humanize_bytes(bytes):
    bytes = float(bytes)
    if bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fGB' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fMB' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fKB' % kilobytes
    else:
        size = '%dB' % bytes
    return size


def check_conf_dir(name):
    savedir = expanduser("~/{}".format(name))
    if not os.path.exists(savedir):
        os.mkdir(savedir)
    return savedir


def make_html(c):
    return markdown.markdown(c)


def send_telegram(message):
    return requests.post('https://api.telegram.org/bot272606808:AAFkyO_YmBswOLeNZ2AV3WsYeaeTrW6yPDU/sendMessage',
                         data={'chat_id': '-172968462', 'text': message})