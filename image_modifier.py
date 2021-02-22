# -*- coding: utf-8 -*-
import threading
from PIL import Image

class ImageModifier:
    """The ImageModifier class makes it easy to modify a pillow Image.
    Only one image is usable by instance, and it uses the threading module for
    faster processing. The image is modified following parameters such as Hue,
    Saturation, Constrast, etc.
    """
    
    
    def __init__(self, image: Image.Image, tiles_x=8, tiles_y=8):
        self.image = image
        self.tiles_x = tiles_x
        self.tiles_y = tiles_y
        
        
    def modify_image(self, hsvc: tuple, bw: int):
        
        
        
        if hsvc == (0, 0, 0, 0) and bw == 0:
            return self.image
        
        width = self.image.width
        height = self.image.height
        tiles_x = self.tiles_x
        tiles_y = self.tiles_y
        
        size_x = int(width/tiles_x)
        size_y = int(height/tiles_y)
        
        threads = []
        
        for t_y in range(tiles_y):
            for t_x in range(tiles_x):
                x1 = t_x*size_x
                y1 = t_y*size_y
                x2 = ((t_x+1)*size_x)
                y2 = ((t_y+1)*size_y)
                t = threading.Thread(target=lambda:self.modify_tile(x1, y1,
                                                                    x2, y2,
                                                                    hsvc, bw))
                threads.append(t)
                t.start()
        
        for t in threads:
            t.join()
            
        return self.image
    
    
    def modify_tile(self, x1, y1, x2, y2, hsvc, bw):
        for y in range(y1, y2):
            for x in range(x1, x2):
                self.modify_pixel((x, y), hsvc, bw)
        
        
    def modify_pixel(self, coords, hsvc: tuple, bw: int):
        
        pixel = self.image.getpixel(coords)

        out = pixel
        
        hue, sat, val, cont = hsvc
        
        if bw == 1:
            # value = int((pixel[0]+pixel[1]+pixel[2])/3)
            value = int(0.64*out[0]+0.32*out[1]+0.02*out[2])
            out = [value, value, value]
        
        if val != 0:
            fact = val/100+1
            out = [int(out[0]*fact), int(out[1]*fact), int(out[2]*fact)]
            
        if cont != 0:
            red = out[0]
            green = out[1]
            blue = out[2]
            cont_rat = cont/100

            red += (red-128)*cont_rat
            green += (green-128)*cont_rat
            blue += (blue-128)*cont_rat

            
            out = [int(red), int(green), int(blue)]
        
        if len(out) < 4 and 'A' in self.image.getbands():
                out.append(pixel[3])
                
                
        # if hsv != (0, 0, 0):
        
        out = tuple(out)
        
        self.image.putpixel(coords, out)