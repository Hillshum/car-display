from typing import OrderedDict
import datetime
import requests

PATH = "http://192.168.1.254/"

CONNECT_PARAMS = OrderedDict(custom=1, cmd=8001)
DISCONNECT_PARAMS = OrderedDict(custom=1, cmd=8002)
SET_CLOCK_PARAMS = OrderedDict(custom=1, cmd=3034)

def update_time_calls():
    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%-d_%H:%M:%S")
    print(date_time)
    SET_CLOCK_PARAMS['str'] =  date_time
    connect = requests.get(PATH, params=CONNECT_PARAMS)
    print(connect.content)
    sett = requests.get(PATH, params=SET_CLOCK_PARAMS)
    print(sett.content)
    disconnect = requests.get(PATH, DISCONNECT_PARAMS)
    print(disconnect.content)

