
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

USAGE_AVERAGE_COUNT = 10


def weighted_average(items):
    total = 0
    total_time = 0

    for index, item in enumerate(items):
        if index == 0:
            continue

        previous_time = items[index -1].time
        time_delta = item.time -previous_time
        
        total_time += time_delta

        total += item.value.magnitude * time_delta

    return ( total / time_delta ) * items[-1].value.units



def get_connection():
    if os.getenv('CARPI_MOCK'):
        return None


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

        self._fuel_readings = []
        self._maf_readings = []
        self._speed_readings = []

        self.connection.watch(obd.commands.MAF, lambda x : self._maf_readings.append(x))
        self.connection.watch(obd.commands.SPEED, lambda x : self._speed_readings.append(x))
        self.connection.watch(obd.commands.FUEL_LEVEL, lambda x : self._fuel_readings.append(x))

        self.connection.start()


    def get_fuel_usage(self, connection):

        maf = weighted_average(self._maf_readings[-USAGE_AVERAGE_COUNT:])
        speed = weighted_average(self._speed_readings[-USAGE_AVERAGE_COUNT:])

        fuel_rate = maf / FUEL_MIXTURE 
        fuel_rate_by_volume = fuel_rate * GASOLINE_DENSITY

        inverted_fuel_volume = fuel_rate_by_volume ** -1

        distance_per_volume = inverted_fuel_volume * speed

        mpg = distance_per_volume.to('mile/gallon')

        return mpg


    def get_dte(self, connection, current_mpg):
        fuel = self._fuel_readings[-1].value.magnitude

        gallons_remaining = fuel * TANK_SIZE_GALLONS

        dte = gallons_remaining * STATIC_MPG / 100



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

        self._fuel_readings = self._fuel_readings[-USAGE_AVERAGE_COUNT:]
        self._maf_readings = self._maf_readings[-USAGE_AVERAGE_COUNT:]

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

