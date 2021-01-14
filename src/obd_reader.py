
import os
import random
import time
import traceback

import obd
import pint

ureg = pint.UnitRegistry()

FUEL_MIXTURE = 14.7

GASOLINE_DENSITY = 1.335291761 * obd.Unit.centimeter ** 3 / obd.Unit.gram

if os.getenv('CARPI_MOCK'):
    connection = None
else:
    connection = obd.OBD()

def get_fuel_usage():
    maf = connection.query(obd.commands.MAF).value
    print(maf)
    speed = connection.query(obd.commands.SPEED).value
    print(speed)
    fuel_rate = maf / FUEL_MIXTURE

    fuel_rate_by_volume = fuel_rate * GASOLINE_DENSITY

    inverted_fuel_volume = fuel_rate_by_volume ** -1

    distance_per_volume = inverted_fuel_volume * speed

    mpg = distance_per_volume.to('mile/gallon')

    return mpg.m


def get_dte():
    return random.random() * 400


def get_mock():
    print('producing mock values')
    return { 
        'current': random.random() * 40 + 10,
        'dte':  random.random() * 400,
    }

def read_obd():
    if os.getenv('CARPI_MOCK'):
        return get_mock()
    
    current = get_fuel_usage()
    print(current)
    dta = get_dte()

    return { 'current': current, 'dte': dta}


def update_loop(queue):
    while True:
        try:
            latest_values = read_obd()
            print(latest_values)
            queue.put(latest_values)

            time.sleep(3)
        except Exception as e:
            print(e)

