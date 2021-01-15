
import os
import random
import time
import traceback

import obd
import pint


FUEL_MIXTURE = 14.7

TANK_SIZE_GALLONS = 13.2 * obd.Unit.gallon

GASOLINE_DENSITY = 1.335291761 * obd.Unit.centimeter ** 3 / obd.Unit.gram

STATIC_MPG = 25 * obd.Unit.mile / obd.Unit.gallon

connection = None

def get_connection():
  if os.getenv('CARPI_MOCK'):
    return None

  global connection

  if connection:
    return connection


  connection = obd.OBD()

  return connection


def get_fuel_usage(connection):
    maf = connection.query(obd.commands.MAF).value
    print(maf)
    speed = connection.query(obd.commands.SPEED).value
    print(speed)
    fuel_rate = maf / FUEL_MIXTURE

    fuel_rate_by_volume = fuel_rate * GASOLINE_DENSITY

    inverted_fuel_volume = fuel_rate_by_volume ** -1

    distance_per_volume = inverted_fuel_volume * speed

    mpg = distance_per_volume.to('mile/gallon')

    return mpg


def get_dte(connection, current_mpg):
    fuel = connection.query(obd.commands.FUEL_LEVEL).value.magnitude

    gallons_remaining = fuel * TANK_SIZE_GALLONS
    print(gallons_remaining)

    dte = gallons_remaining * STATIC_MPG / 100


    print(dte)

    return dte


def get_mock():
    print('producing mock values')
    return { 
        'current': random.random() * 40 + 10,
        'dte':  random.random() * 400,
    }

def read_obd():
    connection = get_connection()
    if connection is None:
        return get_mock()
    
    current = get_fuel_usage(connection)
    print(current)
    dta = get_dte(connection, current)

    return { 'current': current.m, 'dte': dta.m}


def update_loop(queue):
    while True:
        try:
            latest_values = read_obd()
            print(latest_values)
            queue.put(latest_values)

            time.sleep(1)
        except Exception as e:
            print(e)

