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

    def __init__(self, master, kueue):
        tk.Frame.__init__(self, master)
        self.master = master

        self.queue = kueue

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

        self.current = FormatLabel(self.fuel, format="{:.1f} MPG", fg=TEXT_COLOR,
            textvariable=self.data['current'], bg=BACKGROUND_COLOR)
        self.current.pack(side=tk.LEFT, padx=20)

        self.fuel.pack(expand=1)

        self.weather = FormatLabel(format="{} °F", textvariable=self.data['temp'], bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR)
        self.weather.pack(expand=1)

        self.pack(fill=tk.BOTH, expand=1)

    def update_current(self):

        while not self.queue.empty():
            for key, value in self.queue.get().items():
                self.data[key].set(value)

        self.after(1000, self.update_current)

    def update_clock(self):
        now = time.strftime("%-H:%M", time.localtime())
        self.time.configure(text=now)
        self.after(500, self.update_clock)


setproctitle.setproctitle("carpigui")

root = tk.Tk()

root.geometry(RESOLUTION)

kueue = queue.Queue()

app = Window(root, kueue)
app.configure(bg=BACKGROUND_COLOR)

app.update_clock()
app.update_current()


update_thread = threading.Thread(target=obd_reader.update_loop, args=(kueue,))
update_thread.start()

def sigint_handler(sig, frame):
    root.quit()
    root.update()

signal.signal(signal.SIGINT, sigint_handler)
root.mainloop()

