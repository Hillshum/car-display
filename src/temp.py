import os
import RPi.GPIO as GPIO

#  Set Pullup mode on GPIO4 first.
GPIO_PIN_NUMBER=4
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN_NUMBER, GPIO.IN, pull_up_down=GPIO.PUD_UP)


INTERIOR_PROBE = '28-3c01f0957933'

def read_interior():
    device_data_file = '/sys/bus/w1/devices/' + INTERIOR_PROBE + '/w1_slave'
    deviceid = 'internal'
    rtn = {deviceid: {}}

    if os.path.isfile(device_data_file):
        try:
            f = open(device_data_file, "r")
            data = f.read()
            f.close()
            if "YES" in data:
                (discard, sep, reading) = data.partition(' t=')
                rtn[deviceid]['temp_c'] = float(reading) / float(1000.0)
            else:
                rtn[deviceid]['error'] = 'No YES flag: bad data.'
        except Exception as e:
            rtn[deviceid]['error'] = 'Exception during file parsing: ' + str(e)
    else:
        rtn[deviceid]['error'] = 'w1_slave file not found.'

    return rtn