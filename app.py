#!/bin/env python3
import random
import time

import setproctitle

import tkinter as tk
import tkinter.font as tkFont

import signal

RESOLUTION = "693x476"

FUEL_CONSUMPTION = 28.400001

DTE = 208.343

TEMP = 81

BACKGROUND_COLOR = 'black'
TEXT_COLOR = 'white'


def get_fuel_usage():
    return random.random() * 40 + 10

def get_dta():
    return random.random() * 400

class Window(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master

        default_font = tkFont.nametofont('TkDefaultFont')
        default_font.configure(size=55, family='Arial')

        self.master.title("GUI")
        self.master['bg'] = BACKGROUND_COLOR
        self.time = tk.Label(text="")
        self.time['bg'] = BACKGROUND_COLOR
        self.time['fg'] = TEXT_COLOR
        self.time.pack(expand=1)

        self.fuel = tk.Frame(master, bg=BACKGROUND_COLOR)


        self.dta = tk.Label(self.fuel, text="{:.0f} mi".format(DTE), fg=TEXT_COLOR,
            bg=BACKGROUND_COLOR)
        self.dta.pack(side=tk.RIGHT, padx=20)

        self.current = tk.Label(self.fuel, text="{:.1f} MPG".format(FUEL_CONSUMPTION), fg=TEXT_COLOR,
            bg=BACKGROUND_COLOR)
        self.current.pack(side=tk.LEFT, padx=20)

        self.fuel.pack(expand=1)

        self.weather = tk.Label(text="{} °F".format(TEMP), bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR)
        self.weather.pack(expand=1)

        self.pack(fill=tk.BOTH, expand=1)

    def update_current(self):
        self.current.configure(text=get_fuel_usage())
        self.after(1000, self.update_current)

    def update_clock(self):
        now = time.strftime("%-H:%M", time.localtime())
        self.time.configure(text=now)
        self.after(1000, self.update_clock)


setproctitle.setproctitle("carpigui")

root = tk.Tk()

root.geometry(RESOLUTION)

app = Window(root)
app.configure(bg=BACKGROUND_COLOR)

app.update_clock()
#app.update_current()

def sigint_handler(sig, frame):
    root.quit()
    root.update()

signal.signal(signal.SIGINT, sigint_handler)
root.mainloop()

