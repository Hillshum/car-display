#!/bin/env python3

import signal
import queue
import random
import time
import threading

import setproctitle

import tkinter as tk
import tkinter.font as tkFont

import obd_reader
from format_label import FormatLabel

RESOLUTION = "693x476"

FUEL_CONSUMPTION = 28.400001

DTE = 208.343

TEMP = 81.0

BACKGROUND_COLOR = 'black'
TEXT_COLOR = 'gray'


class Window(tk.Frame):

    def __init__(self, master, get_values):
        tk.Frame.__init__(self, master)
        self.master = master

        self.get_values = get_values

        self.data = {
            'current': tk.DoubleVar(value=FUEL_CONSUMPTION),
            'dte': tk.DoubleVar(value=DTE),
            'temp': tk.DoubleVar(value=TEMP)
        }

        default_font = tkFont.nametofont('TkDefaultFont')
        default_font.configure(size=55, family='Arial')

        self.master.title("GUI")
        self.master['bg'] = BACKGROUND_COLOR
        self.time = FormatLabel(text="")
        self.time['bg'] = BACKGROUND_COLOR
        self.time['fg'] = TEXT_COLOR
        self.time.pack(expand=1)

        self.fuel = tk.Frame(master, bg=BACKGROUND_COLOR)


        self.dte = FormatLabel(self.fuel, textvariable=self.data['dte'], fg=TEXT_COLOR,
            bg=BACKGROUND_COLOR, format="{:.0f} mi")
        self.dte.pack(side=tk.RIGHT, padx=20)

        self.current = FormatLabel(self.fuel, format="{:.0f} MPG", fg=TEXT_COLOR,
            textvariable=self.data['current'], bg=BACKGROUND_COLOR)
        self.current.pack(side=tk.LEFT, padx=20)

        self.fuel.pack(expand=1)

        self.weather = FormatLabel(format="{} °F", textvariable=self.data['temp'], bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR)
        self.weather.pack(expand=1)

        self.pack(fill=tk.BOTH, expand=1)

    def update_current(self):

        try:
            values = self.get_values()
            for key, value in values.items():
                self.data[key].set(value)
        except Exception as e:
            print('unable to get values', e)

        self.after(100, self.update_current)

    def update_clock(self):
        now = time.strftime("%-H:%M", time.localtime())
        self.time.configure(text=now)
        self.after(500, self.update_clock)


setproctitle.setproctitle("carpigui")

root = tk.Tk()

root.geometry(RESOLUTION)

reader = obd_reader.Reader()

app = Window(root, reader.read_obd)
app.configure(bg=BACKGROUND_COLOR)

app.update_clock()

app.after(10000, app.update_current)




def sigint_handler(sig, frame):
    root.quit()
    root.update()

signal.signal(signal.SIGINT, sigint_handler)
root.mainloop()

