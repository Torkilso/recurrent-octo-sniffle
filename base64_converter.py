import base64 as b64
import re
# Inspo https://stackoverflow.com/questions/41957490/send-canvas-image-data-uint8clampedarray-to-flask-server-via-ajax


# this method converts a base 64 string to an image
# img_string is an string representation of an image
def convertToImg(img_string, equation):
    img_data = b64.standard_b64decode(re.sub('^data:image/.+;base64,', '', img_string))
    file = './bitmap_data/' + equation + '.png'
    #print("Image data: ", img_data)
    with open(file, 'wb') as fh: # filehandler
        fh.write(img_data)