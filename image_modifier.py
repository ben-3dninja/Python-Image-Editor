# -*- coding: utf-8 -*-
import threading
from PIL import Image


class ImageModifier:
    """The ImageModifier class makes it easy to modify a pillow Image.
    Only one image is usable per instance and it is modified following
    given Hue, Saturation, Constrast, etc. To make processing fast enough,
    the threading module is required.
    """
    
    
    def __init__(self, image: Image.Image, tiles_x=8, tiles_y=8):
        """Constructor for the image modifier. Takes as arguments :
        - The image to be modified
        - The number of tiles horizontally (each tile is a part of the image
        that is processed by a single thread)
        - The number of tiles vertically.
        """
        if image.mode != "RGB" and image.mode != "RGBA":
            image = image.convert("RGB")
        self.image = image
        self.tiles_x = tiles_x
        self.tiles_y = tiles_y
    
    
    def modify_image(self, hsvc: tuple, bw: int):
        """Modifies the image following :
        1. Hue Saturation Value and Contrast given in a tuple (as percentages)
        2. Whether the image is Black and White or not (integer - 0/1).
        """

        # Checking that at least some values are set
        if hsvc == (0, 0, 0, 0) and bw == 0:
            return self.image # If not returning the unmodified image
        
        width = self.image.width
        height = self.image.height
        tiles_x = self.tiles_x
        tiles_y = self.tiles_y
        
        # Setting the tile height and width
        size_x = int(width/tiles_x)
        last_x = width % tiles_x # Last tile size
        size_y = int(height/tiles_y)
        last_y = height % tiles_y # Last tile size
        
        threads = []
        
        # Processing each tile using threading

        # Here each loop is added 1 iteration if there is a last
        # uncompleted tile
        for t_y in range(tiles_y+int(last_y != 0)):
            for t_x in range(tiles_x+1+int(last_x != 0)):
                x1 = t_x*size_x
                y1 = t_y*size_y
                x2 = ((t_x+1)*size_x)
                y2 = ((t_y+1)*size_y)
                # Adding the last tile if there is one
                if t_x == tiles_x:
                    x2 = (t_x*size_x)+last_x
                if t_y == tiles_y:
                    y2 = (t_y*size_y)+last_y
                t = threading.Thread(target=lambda:self.modify_tile(x1, y1,
                                                                    x2, y2,
                                                                    hsvc, bw))
                threads.append(t)
                t.start()
        
        # Joining all the threads
        for t in threads:
            t.join()
        
        # Returning the final image
        return self.image
    
    
    def modify_tile(self, x1, y1, x2, y2, hsvc, bw):
        """Modifies the tile. Takes as arguments :
        - The tile's top left corner's coordinates
        - The tile's bottom right corner's coordinates
        - A tuple containing Hue Saturation Value Contrast (as percentages)
        - The Black and White checkbox' value (1/0)
        """
        for y in range(y1, y2):
            for x in range(x1, x2):
                self.modify_pixel((x, y), hsvc, bw)
    
    
    def modify_pixel(self, coords, hsvc, bw):
        """Modifies a single pixel of the image. Takes as arguments :
        - The pixel's coordinates (x and y tuple)
        - A tuple containing Hue Saturation Value Contrast (as percentages)
        - The Black and White checkbox' value (1/0)
        """
        pixel = self.image.getpixel(coords)

        out = pixel
        
        hue, sat, val, cont = hsvc
        
        # Black and white is handled first
        if bw == 1:
            # Defining a medium value that will be applied to all 3 RGB
            # components, taking in account human's color perception
            value = int(0.64*out[0]+0.32*out[1]+0.02*out[2])
            out = [value, value, value]
        
        # Then hue
        if hue != 0:
            # Defining the hue ratio, that will be useful when determining
            # the proportion of each RGB component
            huer = hue / 100

            # Defining the proportion of each component depending on
            # the hue ratio. (the proportion will be multiplied to
            # the pixel's component value)
            if huer < 1/6:
                redr = 1
                greenr = hue / (1/6)
                bluer = 0
            elif huer < 1/3:
                redr = 1 - ((hue - (1/6)) / (1/6))
                greenr = 1
                bluer = 0
            elif huer < 1/2:
                redr = 0
                greenr = 1
                bluer = (hue - (1/3)) / (1/6)
            elif huer < 2/3:
                redr = 0
                greenr = 1 - ((hue - (1/2)) / (1/6))
                bluer = 1
            elif huer < 5/6:
                redr = (hue - (2/3)) / (1/6)
                greenr = 0
                bluer = 1
            elif huer <= 1:
                redr = 1
                greenr = 0
                bluer = 1 - ((hue - (5/6)) / (1/6))

            # Multiplying each component with its corresponding ratio and
            # adding compensation to shift
            rgb = [redr, greenr, bluer]
            out = [int(out[i]*rgb[i]) for i in range(0, 3)]
        
        # Then saturation
        if sat != 0:
            fact = sat/100
            average = (out[0]+out[1]+out[3])/3
            red = out[0]+(out[0]-average)*fact
            green = out[1]+(out[1]-average)*fact
            blue = out[2]+(out[2]-average)*fact

            out = [int(e) for e in [red, green, blue]]


        # Then value
        if val != 0:
            fact = val/100+1
            out = [int(out[0]*fact), int(out[1]*fact), int(out[2]*fact)]
        
        # Then constrast
        if cont != 0:
            red = out[0]
            green = out[1]
            blue = out[2]
            cont_rat = cont/100 # Defining the constrast ratio

            red += (red-128)*cont_rat
            green += (green-128)*cont_rat
            blue += (blue-128)*cont_rat
            
            out = [int(red), int(green), int(blue)]
        
        # If the image had an alpha channel, then adds it back
        if len(out) < 4 and 'A' in self.image.getbands():
                out.append(pixel[3])
        
        out = tuple(out)
        
        # Putting the modified pixel at its place in the image
        self.image.putpixel(coords, out)