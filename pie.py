# -*- coding: utf-8 -*-

from tkinter import Tk, Frame, LabelFrame, Label, Menu, Grid, Button
from tkinter import DISABLED, NORMAL
from tkinter.font import Font
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
from image_modifier import ImageModifier
from buttons import PercentSlider, Checkbox
from copy import copy
from time import time


class PIEApplication:
    """The main class for the Python Image Editor project."""


    def __init__(self, path = None):
        """The application constructor. Takes in argument the path of the
        default image.
        """
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
        """Creates the settings menu."""
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
        """Creates the menu on the top of the window."""
        self.menubar = Menu(self.master)

        # Creating the menus
        self.menu_file = Menu(self.menubar)
        self.menu_edit = Menu(self.menubar)

        # Adding them to the menu bar
        self.menubar.add_cascade(label="File", menu=self.menu_file)
        self.menubar.add_cascade(label="Edit", menu=self.menu_edit)
        
        # Adding the elements

        # File menu
        self.menu_file.add_command(label="Open", command=self.open_image)
        self.menu_file.add_command(label="Save")
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=self.stop)

        # Edit menu
        self.menu_edit.add_command(label="Undo", command=self.undo, state=DISABLED)
        self.undo_image = None
        self.menu_edit.add_command(label="Redo", command=self.redo, state=DISABLED)
        self.redo_image = None
        
        # Adding the menu to the master
        self.master.config(menu=self.menubar)
    

    def update_menu(self):
        """Updates the menu on the top of the window, to gray out
        some possibilities for example."""
        if self.undo_image == None:
            self.menu_edit.entryconfig("Undo", state=DISABLED)
        else:
            self.menu_edit.entryconfig("Undo", state=NORMAL)
        if self.redo_image == None:
            self.menu_edit.entryconfig("Redo", state=DISABLED)
        else:
            self.menu_edit.entryconfig("Redo", state=NORMAL)

    
    def run(self):
        """Runs the application."""
        self.master.mainloop()
    
    
    def open_image(self):
        """Triggered when File > Open is pressed. Asks for a path and opens
        the imagecorresponding image.
        """
        file = askopenfile(mode='r',filetypes=[
            ('PNG', '*.png'), ('JPG', '*jpg')])
        if file != None:
            self.load_image(file.name)
    
    
    def undo(self):
        """Undoes last change."""
        self.redo_image = copy(self.image)
        self.image = copy(self.undo_image)
        self.update_image()
        self.undo_image = None
        self.update_menu()


    def redo(self):
        """Redoes last change."""
        self.undo_image = copy(self.image)
        self.image = copy(self.redo_image)
        self.update_image()
        self.redo_image = None
        self.update_menu()

    
    def update_image(self):
        """Reloads the label with the image attribute."""
        render = ImageTk.PhotoImage(master=self.image_frame, image=self.image)
        self.render = render
        self.imagelabel.configure(image=render)
        self.update_menu()
    
    
    def apply(self):
        """Applies the modifications using the ImageModifier class from
        image_modifier.py.
        """
        self.undo_image = copy(self.image)
        image_modifier = ImageModifier(self.image)
        hsvc = (self.hue.get(), self.sat.get(),
                self.val.get(), self.cont.get())
        image_modifier.modify_image(hsvc, self.bw.get())
        self.update_image()
     
        
    def load_image(self, path):
        """Loads the image at the given path, copies it in the 'original'
        attribute and packs it in the image frame.
        """
        
        self.original = Image.open(path)
        if self.image == None:
            self.imagelabel = Label(master=self.image_frame)
            self.imagelabel.pack(side="top", padx=self.pad, pady=self.pad)
        self.undo_image = copy(self.image)
        self.redo_image = copy(self.image)
        self.image = copy(self.original)
        render = ImageTk.PhotoImage(master=self.image_frame, image=self.image)
        self.render = render
        self.imagelabel.configure(image=render)
        self.update_menu()
    

    def reset(self):
        """Resets the settings sliders and the displayed image."""
        self.undo_image = copy(self.image)
        self.image = copy(self.original)
        self.update_image()
        self.hue.set(0)
        self.sat.set(0)
        self.val.set(0)
        self.cont.set(0)
        self.bw.set(0)
        
    
    def stop(self):
        """Stops the application."""
        self.master.quit()


app = PIEApplication()
app.run()
