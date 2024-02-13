#
# take a picture
#

import board
import espcamera

cam = espcamera.Camera(
    data_pins=board.D,
    pixel_clock_pin=board.PCLK,
    vsync_pin=board.VSYNC,
    href_pin=board.HREF,
    i2c=board.SSCB_I2C(),
    external_clock_pin=board.XCLK,
    reset_pin=board.RESET,
    pixel_format=espcamera.PixelFormat.RGB565,
    frame_size=espcamera.FrameSize.R96X96
    )

cam.colorbar=False # Test 

cam.reconfigure()
bitmap=cam.take(1)
print(type(bitmap))


#
# save RGB565BMP file
#

def RGB565toBMPfile(filename , bitmap):

    import struct
    import ulab.numpy as np


    output_file=open( filename  ,"wb" )

    # _bytes_per_row(width)
    pixel_bytes = 3* bitmap.width
    padding_bytes = (4 - (pixel_bytes % 4)) % 4
    bytes_per_row = pixel_bytes + padding_bytes

    filesize = 66 + bitmap.height * bytes_per_row


    # _write_bmp_header(output_file, filesize)
    output_file.write(bytes("BM", "ascii"))
    output_file.write(struct.pack("<I", filesize))
    output_file.write(b"\00\x00")
    output_file.write(b"\00\x00")
    output_file.write(struct.pack("<I", 66))


    #  _write_dib_header(output_file, width, height)
    output_file.write(struct.pack("<I", 40))
    output_file.write(struct.pack("<I", bitmap.width))
    output_file.write(struct.pack("<I", bitmap.height))
    output_file.write(struct.pack("<H", 1))
    output_file.write(struct.pack("<H", 16))  #bits per pixel
    for _ in range(24):
        output_file.write(b"\x00")

    output_file.write(b"\x00\xF8\x00\x00")  #RED mask
    output_file.write(b"\xE0\x07\x00\x00")  #GREEN mask
    output_file.write(b"\x1F\x00\x00\x00")  #BLUE mask

    #  _write_pixels(output_file, bitmap)
    swapped = np.frombuffer(bitmap, dtype=np.uint16)
    swapped.byteswap(inplace=True)
    output_file.write(swapped)


    output_file.close()

    return



print('Saving bitmap')

RGB565toBMPfile('/static/camera.bmp'  , bitmap )



#
# https://docs.circuitpython.org/projects/httpserver/en/latest/examples.html#id6
#
import socketpool
import wifi

from adafruit_httpserver import Server, MIMETypes


MIMETypes.configure(
    default_to="text/plain",
    # Unregistering unnecessary MIME types can save memory
    keep_for=[".html", ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".ico"],
    # If you need to, you can add additional MIME types
    register={".foo": "text/foo", ".bar": "text/bar"},
)

pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)

# You don't have to add any routes, by default the server will serve files
# from it's root_path, which is set to "/static" in this example.

# If you don't set a root_path, the server will not serve any files.

server.serve_forever(str(wifi.radio.ipv4_address))
