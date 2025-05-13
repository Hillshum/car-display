#!/bin/env python3

import signal
import queue
import random
import subprocess
import time
import threading
from math import nan

import setproctitle

import tkinter as tk
import tkinter.font as tkFont
import pint

import obd_reader
from format_label import FormatLabel
import yicam
import temp

RESOLUTION = "693x476"

FUEL_CONSUMPTION = 28.400001

DTE = 208.343

TEMP = 81.0

DASHCAM_INITIAL_DELAY = 30 * 1000 # 30 seconds

DASHCAM_RETRY_DELAY = 1000 * 60 * 60

BACKGROUND_COLOR = 'black'
TEXT_COLOR = 'gray'


ureg = pint.UnitRegistry()

IP_CMD = r"ip addr show wlan0 | grep -Po 'inet \K[\d.]+'"

def get_ip():
    p = subprocess.run(IP_CMD, capture_output=True, shell=True)
    return p.stdout.decode().strip()

def INITIAL_DATA():
    print('creating initial data')
    return {
        'current': tk.DoubleVar(),
        'dte': tk.DoubleVar(),
        'gear': tk.DoubleVar(),
        'target_rpm': tk.DoubleVar(),
        'rpm': tk.IntVar(),
        'coolant_temp': tk.DoubleVar(),
}

class Window(tk.Frame):

    def __init__(self, master, get_values):
        tk.Frame.__init__(self, master)
        self.master = master

        self.get_values = get_values

        self.data = dict(INITIAL_DATA())

        self.temp = {
            'interior': tk.DoubleVar(),
        }

        default_font = tkFont.nametofont('TkDefaultFont')
        default_font.configure(size=55, family='Arial')

        self.master.title("GUI")
        self.master['bg'] = BACKGROUND_COLOR

        self.top = tk.Frame(master, bg=BACKGROUND_COLOR)
        self.time = FormatLabel(self.top, text="")
        self.time['bg'] = BACKGROUND_COLOR
        self.time['fg'] = TEXT_COLOR
        self.time.pack(side=tk.LEFT, padx=20)

        self.top.pack(expand=1)

        self.fuel = tk.Frame(master, bg=BACKGROUND_COLOR)

        self.dte = FormatLabel(self.fuel, textvariable=self.data['dte'], fg=TEXT_COLOR,
            bg=BACKGROUND_COLOR, format="{:.0f} mi")
        self.dte.pack(side=tk.RIGHT, padx=20)

        self.current = FormatLabel(self.fuel, format="{:3.0f} MPG", fg=TEXT_COLOR,
            textvariable=self.data['current'], bg=BACKGROUND_COLOR)
        self.current.pack(side=tk.LEFT, padx=20)

        self.fuel.pack(expand=1)

        self.third = tk.Frame(master, bg=BACKGROUND_COLOR)

        self.gear = FormatLabel(self.third, format="{:.0f}", textvariable=self.data['gear'], bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR)
        self.gear.pack(side=tk.LEFT, padx=20)

        self.coolant_temp = FormatLabel(self.third, format="{:2.0f}°C", fg=TEXT_COLOR, textvariable=self.data['coolant_temp'], bg=BACKGROUND_COLOR)

        self.coolant_temp.pack(side=tk.RIGHT, padx=20)

        self.current_rpm = FormatLabel(self.third, format="{:4d}", fg=TEXT_COLOR, textvariable=self.data['rpm'], bg=BACKGROUND_COLOR )

        self.current_rpm.pack(side=tk.LEFT, padx=20)

        self.third.pack(expand=1, fill=tk.X)

        self.pack(fill=tk.BOTH, expand=1)

        self.ip = tk.Label(self, text="192.168.0", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        self.ip['font'] = 'Arial', 25
        self.ip.pack(side=tk.BOTTOM, padx=20)

    def update_ip(self):
        try:
            self.ip['text'] = get_ip()
        except Exception as e:
            print('unable to get ip', e)

        finally:
            self.after(2000, self.update_ip)

    def update_current(self):

        try:
            values = self.get_values()
            for key, value in values.items():
                self.data[key].set(value)
        except Exception as e:
            print('unable to get values', e)
            defaults = INITIAL_DATA()
            for key, value in self.data.items():
                self.data[key].set(defaults[key].get())

        finally:
            self.after(100, self.update_current)

    def update_clock(self):
        now = time.strftime("%-H:%M", time.localtime())
        self.time.configure(text=now)
        self.after(500, self.update_clock)

    def update_temp(self):
        try:
            reading = temp.read_interior()
            print(reading)
            interior = reading['internal']
            deg_c = ureg.Quantity(interior['temp_c'], 'celsius')
            deg_f = deg_c.to('fahrenheit').magnitude
            self.temp['interior'].set( deg_f)
        except:
            self.temp['interior'].set(nan)
        finally:
            self.after(600, self.update_temp)


setproctitle.setproctitle("carpigui")

root = tk.Tk()

root.geometry(RESOLUTION)

reader = obd_reader.Reader()

app = Window(root, reader.read_obd)
app.configure(bg=BACKGROUND_COLOR)

app.update_clock()
app.update_temp()
app.update_ip()

app.after(300, app.update_current)


def update_dashcam():
    try:
        yicam.update_time_calls()
    except Exception as e:
        print('unable to update dashcam', e)
    finally:
        app.after(DASHCAM_RETRY_DELAY, update_dashcam)


app.after(DASHCAM_INITIAL_DELAY, update_dashcam)


def sigint_handler(sig, frame):
    root.quit()
    root.update()

signal.signal(signal.SIGINT, sigint_handler)
root.mainloop()
