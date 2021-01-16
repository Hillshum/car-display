
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

obd.logger.setLevel(obd.logging.DEBUG)

def get_connection():
    if os.getenv('CARPI_MOCK'):
        return None

    global connection

    if connection:
        return connection



    print("creating new connection")
    connection = obd.Async()
    print(connection)

    return connection

class Reader():

    def __init__(self):
        if os.getenv('CARPI_MOCK'):
            return

        self.connection = get_connection()

        print("watching with connection {}".format(self.connection))

        self.connection.watch(obd.commands.MAF)
        self.connection.watch(obd.commands.SPEED)
        self.connection.watch(obd.commands.FUEL_LEVEL)

        self.connection.start()

    def get_fuel_usage(self, connection):
        print("querying with connection {}".format(connection))
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


    def get_dte(self, connection, current_mpg):
        fuel = connection.query(obd.commands.FUEL_LEVEL).value.magnitude

        gallons_remaining = fuel * TANK_SIZE_GALLONS
        print(gallons_remaining)

        dte = gallons_remaining * STATIC_MPG / 100


        print(dte)

        return dte


    def get_mock(self):
        print('producing mock values')
        return { 
            'current': random.random() * 40 + 10,
            'dte':  random.random() * 400,
        }

    def read_obd(self):
        # connection = get_connection()
        # if connection is None:
        #     return self.get_mock()
        
        connection = self.connection

        current = self.get_fuel_usage(connection)
        # print(current)
        dta = self.get_dte(connection, current)

        return { 'current': current.m, 'dte': dta.m}





# def update_loop(queue):
#     while True:
#         try:
#             latest_values = read_obd()
#             print(latest_values)
#             queue.put(latest_values)

#             time.sleep(1)
#         except Exception as e:
#             print(e)

