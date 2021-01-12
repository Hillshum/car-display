import random
import time

def get_fuel_usage():
    return random.random() * 40 + 10

def get_dta():
    return random.random() * 400

def read_obd():
    current = get_fuel_usage()
    dta = get_dta()

    return { 'current': current, 'dta': dta}


def update_loop(queue):
    while True:
        try:
            latest_values = read_obd()
            print(latest_values)
            queue.put(latest_values)

            time.sleep(3)
        except Exception as e:
            print(e)

