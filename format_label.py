# From https://stackoverflow.com/questions/59408126/tkinter-formatting-doublevars-for-display


import tkinter as tk


class FormatLabel(tk.Label):

    def __init__(self, master=None, cnf={}, **kw):

        # default values
        self._format = '{}'  
        self._textvariable = None

        # get new format and remove it from `kw` so later `super().__init__` doesn't use them (it would get error message)
        if 'format' in kw:
            self._format = kw['format']
            del kw['format']

        # get `textvariable` to assign own function which set formatted text in Label when variable change value
        if 'textvariable' in kw:
            self._textvariable = kw['textvariable']
            self._textvariable.trace('w', self._update_text)
            del kw['textvariable']

        # run `Label.__init__` without `format` and `textvariable`
        super().__init__(master, cnf={}, **kw)

        # update text after running `Label.__init__`
        if self._textvariable:
            #self._update_text(None, None, None)
            self._update_text(self._textvariable, '', 'w')

    def _update_text(self, a, b, c):
        """update text in label when variable change value"""
        self["text"] = self._format.format(self._textvariable.get())
