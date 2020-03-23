import os
import glob
import time
import datetime
import ctypes


def date_string():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m%d')
    return st


def message_box(title, text, style):
    ctypes.windll.user32.MessageBoxW(0, text, title, style)
    return None


def system_error_decoder(code):
    codes ={
        0: 'SUCCESS',
        1: 'ERROR_INVALID_FUNCTION',
        2: 'ERROR_FILE_NOT_FOUND',
        3: 'ERROR_PATH_NOT_FOUND',
        4: 'ERROR_TOO_MANY_OPEN_FILES',
        5: 'ERROR_ACCESS_DENIED'
        }
    try:
        return "{}: {}".format(codes[code], code)
    except:
        return "System Error Code: {}".format(code)
