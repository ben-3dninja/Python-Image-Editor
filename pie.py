# -*- coding: utf-8 -*-

from tkinter import Tk, Frame, LabelFrame, Label, Menu, Grid, Button
from tkinter.font import Font
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
from image_modifier import ImageModifier
from buttons import PercentSlider, Checkbox
from copy import copy
from time import time


    

class PIEApplication:
    """The main class for the Python Image Editor project"""
    
    def __init__(self, path = None):
        self.master = Tk() # The root tkinter Tk object
        self.width = 720 # The minimum window width
        self.height = 500 # The minimum window height
        self.title = 'Python PIE' # The window title
        self.pad = 5 # The default padding for widgets
        
        
        # Defining the dictionnary containing the fonts
        self.fonts = {'title': Font(self.master, font="terminal", size=30)}
        
        # Applying title and minimum size
        self.master.title(self.title)
        self.master.minsize(self.width, self.height)
        
        # Configuring grid geometry manager
        Grid.rowconfigure(self.master, 0, weight=1)
        Grid.columnconfigure(self.master, 0, weight=1) # Column 0 : Image
        Grid.columnconfigure(self.master, 1, weight=0) # Column 1 : Settings
        
        # Creating the menu
        self.create_menu()
        
        # Defining image frame (will contain the image)
        self.image_frame = Frame(master=self.master)
        self.image_frame.grid(row=0, column=0, sticky="W")
        
        self.image = None
        
        # Verifying if a path has been passed as a constructor parameter
        if path != None:
            # If yes, loading image from path
            self.load_image(path)
        
        # Creating the settings frame
        self.create_settings()
    
    
    def create_settings(self):
        
        # Defining the settings frame (will contain all the settings)
        settings_frame = Frame(master=self.master)
        settings_frame.grid(row=0, column=1, sticky="E")
        
        # Defining the "Settings" label at the top of the frame 
        settings_label = Label(settings_frame, text="Settings",
                                   font=self.fonts['title'])
        settings_label.pack(side="top", pady = self.pad)
        
        # Defining the Hue Saturation Value and Constrast frame
        hsvc_frame = LabelFrame(master=settings_frame,
                                    text="H/S/V/C")
        hsvc_frame.pack(side="top", pady=self.pad)
        
        # Defining all four PercentSliders corresponding to HSVC
        self.hue = PercentSlider(master=hsvc_frame, label="Hue")
        self.sat = PercentSlider(master=hsvc_frame, label="Saturation")
        self.val = PercentSlider(master=hsvc_frame, label="Value")
        self.cont = PercentSlider(master=hsvc_frame, label="Contrast")
        
        filters_frame = LabelFrame(master=settings_frame, text="Filters")
        filters_frame.pack(side="top", pady=self.pad)
        
        self.bw = Checkbox(master=filters_frame, text="Black and White")
        
        # Defining the Apply button that will trigger the image transformation
        apply_button = Button(master=settings_frame, text="Apply",
                              font=self.fonts["title"], command=self.apply)
        apply_button.pack(side="bottom", pady=self.pad, expand=True, fill='x')
        
        reset_button = Button(master=settings_frame, text="Reset",
                              font=self.fonts["title"], command=self.reset)
        reset_button.pack(side="bottom", pady=self.pad, expand=True, fill='x')
        
    
    
    def create_menu(self):
        menubar = Menu(self.master)
        
        menu_file = Menu(menubar)
        menu_file.add_command(label="Open", command=self.open_image)
        menu_file.add_command(label="Save")
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=self.stop)
        menubar.add_cascade(label="File", menu=menu_file)
        
        
        self.master.config(menu=menubar)
    
    
    def run(self):
        self.master.mainloop()
    
    
    def open_image(self):
        
        file = askopenfile(mode='r',filetypes=[
            ('PNG', '*.png'), ('JPG', '*jpg')])
        self.load_image(file.name)
        
    
    
    def update_image(self):
        render = ImageTk.PhotoImage(master=self.image_frame, image=self.image)
        self.render = render
        self.imagelabel.configure(image=render)
    
    
    def apply(self):
        """Applys the modifications to the image using the ImageModifier
        class from the image_modifier module.
        """
        image_modifier = ImageModifier(self.image)
        hsvc = (self.hue.get(), self.sat.get(),
                self.val.get(), self.cont.get())
        begin_time = time()
        image_modifier.modify_image(hsvc, self.bw.get())
        end_time = time()
        print(end_time-begin_time)
        self.update_image()
     
        
    def load_image(self, path):
        """Loads the image at the given path, copying it to the 'original'
        attribute for later reset and packing it in the image frame.
        """
        
        self.original = Image.open(path)
        if self.image == None:
            self.imagelabel = Label(master=self.image_frame)
            self.imagelabel.pack(side="top", padx=self.pad, pady=self.pad)
        self.image = copy(self.original)
        render = ImageTk.PhotoImage(master=self.image_frame, image=self.image)
        self.render = render
        self.imagelabel.configure(image=render)
    
    def reset(self):
        """Resets the settings sliders and the image"""
        self.image = copy(self.original)
        self.update_image()
        self.hue.set(0)
        self.sat.set(0)
        self.val.set(0)
        self.cont.set(0)
        self.bw.set(0)
        
    
    
    def stop(self):
        self.master.quit()


app = PIEApplication("galaxy.jpg")
app.run()
    