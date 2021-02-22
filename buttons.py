# -*- coding: utf-8 -*-

from tkinter import Scale, IntVar, Checkbutton

class PercentSlider(Scale, IntVar):
    """A PercentSlider object is a tkinter Scale coupled with an IntVar,
    ready to deal easily with percentage values,such as brightess or
    contrast.
    """
    
    def __init__(self, master, label: str, default: int=0, from_=-100, to=100):
        self.label = label
        IntVar.__init__(self, master)
        Scale.__init__(self, master, label=self.label, from_=from_, to=to,
                         orient="horizontal")
        self.pack(side="top")
    
    
    def __str__(self):
        return f"{self.label} : {self.get()}"


class Checkbox(Checkbutton, IntVar):
        
    
    def __init__(self, master, text: str, default: int=0):
        self.text = text
        IntVar.__init__(self, master)
        Checkbutton.__init__(self, master, text=self.text)
        self.pack(side="top")
    
    def __str__(self):
        return f"{self.text} : {self.get()}"
    