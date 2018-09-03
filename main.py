#!/usr/bin/python
# opyright (c) 2017 Adafruit Industries
# Author: Carter Nelson, t10471
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import sys
import shutil
import argparse
from time import sleep
from datetime import datetime
from colour import Color

from Adafruit_AMG88xx import Adafruit_AMG88xx
from PIL import Image, ImageDraw

from upload import uploadfiles
from remo import update_setting

NX = 8
NY = 8
COLORDEPTH = 256
IMAGE_DIR = 'images'

class Thermal:

    def __init__(self, args):
        self.interval = args.interval
        self.end = args.end
        self.min = args.min
        self.max = args.max
        self.report = args.report
        self.scale = args.scale
        self.dt = "{0:%Y-%m-%d}".format(datetime.now())
        self.img_dir = self._make_dir()
        self.sensor = Adafruit_AMG88xx()
        # wait for it to boot
        sleep(.1)

    def _make_dir(self):
        shutil.rmtree(os.path.join(os.getcwd(), IMAGE_DIR))
        img_dir = os.path.join(os.getcwd(), IMAGE_DIR, self.dt)
        os.makedirs(img_dir, exist_ok=True)
        return img_dir

    def main(self):
        self._execute()
        while True:
            self._execute()
            if int("{0:%H}".format(datetime.now())) >= self.end:
                break
            sleep(self.interval)
        uploadfiles(self.img_dir)

    def _execute(self):
        pixels = self._make_pixels()
        if self.report:
            return
        self._update_settings(pixels)
        self._save_image(pixels)

    def _make_pixels(self):

        def _constrain(val, min_val, max_val):
            return min(max_val, max(min_val, val))

        def _map(x, in_min, in_max, out_min, out_max):
            return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

        # get sensor readings
        pixels = self.sensor.readPixels()

        if self.report:
            print("Min Pixel = {0} C".format(min(pixels))) 
            print("Max Pixel = {0} C".format(max(pixels)))
            print("Thermistor = {0} C".format(sensor.readThermistor()))

        # output image buffer
        image = Image.new("RGB", (NX, NY), "white")
        draw = ImageDraw.Draw(image)

        # color map
        colors = list(Color("indigo").range_to(Color("red"), COLORDEPTH))
        colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

        # map sensor readings to color map
        MINTEMP = min(pixels) if self.min == None else self.min
        MAXTEMP = max(pixels) if self.max == None else self.max
        pixels = [_map(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]
        return pixels

    def _save_image(self, pixels):
        # create the image
        for ix in range(NX):
            for iy in range(NY):
                draw.point([(ix, iy % NX)], fill=colors[_constrain(int(pixels[ix + NX * iy]), 0, COLORDEPTH - 1)])
        save_path = os.path.join(self.img_dir, "{0:%H:%M:%S}.jpg".format(datetime.now()))
        # scale and save
        image.resize((NX * scale, NY * scale), Image.BICUBIC).save(save_path)

    def _update_settings(self, pixels):
        # TODO
        if False:
            update_settings()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Save image')
    parser.add_argument('-s','--scale', type=int, default=100, help='specify image scale')
    parser.add_argument('--interval', type=int, default=600, help='specify interval')
    parser.add_argument('--end', type=int, default=9, help='specify end time')
    parser.add_argument('--min', type=float, help='specify minimum temperature')
    parser.add_argument('--max', type=float, help='specify maximum temperature')
    parser.add_argument('--report', action='store_true', default=False, help='show sensor information without saving image')
    args = parser.parse_args()
    Thermal(args).main()
