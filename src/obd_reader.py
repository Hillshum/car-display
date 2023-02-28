
from asyncore import read
import os
import random
import time
import datetime
import logging
from logging import handlers



import obd
import pint

ureg = obd.Unit
Q_ = ureg.Quantity
ureg.load_definitions(os.path.expanduser('~/car-display/src/pint_contexts.txt'))

data_logger = logging.getLogger('obd_data')
data_logger.setLevel('INFO')
handler = handlers.TimedRotatingFileHandler('data_logs/obd', when='M', interval=20)
data_logger.addHandler(handler)
# obd.logger.setLevel(obd.logging.DEBUG)
DEVICE_NAME = '/dev/ttyUSB0'

FUEL_MIXTURE = 14.7

# TANK_SIZE_GALLONS = 13.2 * obd.Unit.gallon

# GASOLINE_DENSITY = 1.335291761 * obd.Unit.centimeter ** 3 / obd.Unit.gram

# STATIC_MPG = 25 * obd.Unit.mile / obd.Unit.gallon

USAGE_AVERAGE_COUNT = 10

RPM_MINIMUM = 900 * obd.Unit.rpm

GEARINGS = [
    [200, 210], # add a dummy at the front to make indexing line up
    [127, 155],
    [65, 100],
    [47, 55],
    [39, 43],
    [32, 36],
    [25, 30],
]

def find_gear_from_ratio(ratio):
    for index, (lower, upper) in enumerate(GEARINGS):
        if lower < ratio < upper:
            return index

    return 0


def find_rpm_for_gear(speed, gear):

    ratio = sum(GEARINGS[gear]) / 2

    return speed * ratio



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


    



class Reader():

    def __init__(self):
        if os.getenv('CARPI_MOCK'):
            return

        self._maf_readings = []
        self._speed_readings = []


        try:
            self.connection = self.get_connection()
        except Exception as e:
            print(f'Unable to connect to vehicle {e}')

    def command_logger(self, callback=None):
        def logger(reading):
            dt = datetime.datetime.fromtimestamp(reading.time)
            data_logger.info(f'{dt.isoformat()} {reading.command.name} {reading.value}')
            if callback:
                callback(reading)

        return logger


    def get_connection(self):
        if os.getenv('CARPI_MOCK'):
            return None
        
        print('testing existing connection')
        try:
            if self.connection.is_connected():
                return self.connection
        except Exception:
            pass
        


        print("creating new connection")
        self.connection = obd.Async(DEVICE_NAME)

        if not self.connection.is_connected():
            raise Exception("Unable to connect")

        print("watching with connection {}".format(self.connection))

        self.connection.watch(obd.commands.MAF, self.command_logger(lambda x : self._maf_readings.append(x)))
        self.connection.watch(obd.commands.SPEED, self.command_logger( lambda x : self._speed_readings.append(x)))
        self.connection.watch(obd.commands.FUEL_LEVEL, self.command_logger())
        self.connection.watch(obd.commands.RPM, self.command_logger())
        self.connection.watch(obd.commands.COMMANDED_EQUIV_RATIO, self.command_logger())
        self.connection.watch(obd.commands.COOLANT_TEMP, self.command_logger())

        self.connection.start()

        time.sleep(2)

        return self.connection
        

    def get_target_rpm(self):
        return find_rpm_for_gear(self.connection.query(obd.commands.SPEED).value.magnitude, 6)

    def get_fuel_usage(self):

        maf = weighted_average(self._maf_readings[-USAGE_AVERAGE_COUNT:])
        speed = weighted_average(self._speed_readings[-USAGE_AVERAGE_COUNT:])

        fuel_rate = maf / FUEL_MIXTURE 
        fuel_rate_by_volume = fuel_rate.to('gallon/second', 'gasoline')

        inverted_fuel_volume = fuel_rate_by_volume ** -1

        distance_per_volume = inverted_fuel_volume * speed

        mpg = distance_per_volume.to('mile/gallon')

        return mpg


    def get_dte(self):
        fuel = self.connection.query(obd.commands.FUEL_LEVEL).value

        gallons_remaining = fuel.to('gallons', 'versa')

        dte = gallons_remaining.to('miles', 'versa')

        return dte


    def get_mock(self):
        print('producing mock values')
        return { 
            'current': random.random() * 40 + 10,
            'dte':  random.random() * 400,
            'gear': find_gear_from_ratio(38),
            'target_rpm': find_rpm_for_gear(35, 6),
            'rpm': 3252,
        }
    
    def get_gear(self):
        rpm = self.connection.query(obd.commands.RPM).value
        speed = self.connection.query(obd.commands.SPEED).value

        # if rpm < RPM_MINIMUM:
        #     return 0
        

        try:
            ratio = rpm / speed
        except ZeroDivisionError:
            return 0

        return find_gear_from_ratio(ratio.magnitude)


    def read_obd(self):
        try:
            if os.getenv('CARPI_MOCK'):
                return self.get_mock()

            self.get_connection()

            current = self.get_fuel_usage()
            dta = self.get_dte()

            gear = self.get_gear()

            target = self.get_target_rpm()

            coolant_temp = self.connection.query(obd.commands.COOLANT_TEMP).value.magnitude

            rpm = self.connection.query(obd.commands.RPM).value.magnitude


            self._speed_readings = self._speed_readings[-USAGE_AVERAGE_COUNT:]
            self._maf_readings = self._maf_readings[-USAGE_AVERAGE_COUNT:]


            return {
                'current': current.m,
                'dte': dta.m,
                'gear': gear,
                'target_rpm':  target,
                'rpm': rpm,
                'coolant_temp': coolant_temp,
            }

        except Exception as e:
            print(f'Error reading, {e}')
            # self.connection.close()
            raise e

