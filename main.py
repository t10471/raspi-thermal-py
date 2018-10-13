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
import logging
import yaml
from time import sleep
from datetime import datetime
from colour import Color

from Adafruit_AMG88xx import Adafruit_AMG88xx
from PIL import Image, ImageDraw

from upload import GDriveFactory
from remo import RemoFactory

NX = 8
NY = 8
COLORDEPTH = 256
COF_NAME = 'config.yaml'
IMAGE_DIR = 'images'
LOG_DIR = 'logs'

class Thermal:

    def __init__(self, fname):
        with open(fname, "r") as f:
            config = yaml.load(f)['main']
        self.logger = self._setup_logger(config)
        self.gdrive = GDriveFactory.create(config, fname)
        self.remo = RemoFactory.create(config, fname)
        self.interval = config['interval']
        self.min = config['min']
        self.max = config['max']
        self.report = config['report']
        self.scale = config['scale']
        self.dt = '{0:%Y-%m-%d}'.format(datetime.now())
        m = '{0} {1:%H:%M:%S}'.format(self.dt, datetime.strptime(config['end'], '%H:%M:%S'))
        self.end = datetime.strptime(m, '%Y-%m-%d %H:%M:%S')
        self.img_dir = self._make_dir()
        # color map
        cs = list(Color('indigo').range_to(Color('red'), COLORDEPTH))
        self.colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in cs]
        self.sensor = Adafruit_AMG88xx()
        # wait for it to boot
        sleep(.1)

    def _setup_logger(self, config):
        levels = {'CRITICAL': logging.CRITICAL,
                  'ERROR': logging.ERROR,
                  'WARNING': logging.WARNING,
                  'INFO': logging.INFO,
                  'DEBUG': logging.DEBUG
                  }
        if config['log_level'] not in levels.keys():
            print('{} is invalid log_level'.format(config['log_level']))
            sys.exit(1)
        logger = logging.getLogger('Thermal')
        logger.setLevel(levels[config['log_level']])
        handler_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        os.makedirs(os.path.join(os.getcwd(), LOG_DIR), exist_ok=True)
        p = os.path.join(os.getcwd(), LOG_DIR, '{0:%Y-%m-%d}.log'.format(datetime.now()))
        handler = logging.FileHandler(p, 'w')
        handler.setLevel(levels[config['log_level']])
        handler.setFormatter(handler_format)
        logger.addHandler(handler)

        return logger

    def __str__(self):
        s = 'Thermal (interval: {interval}, end: {end}, img_dir: {img_dir}, min: {min}, max {max}, scale: {scale})'
        return s.format(interval=self.interval, end=self.end, img_dir=self.img_dir,
                        min=self.min, max=self.max, scale=self.scale)

    def _make_dir(self):
        try:
            shutil.rmtree(os.path.join(os.getcwd(), IMAGE_DIR))
        except Exception:
            pass
        img_dir = os.path.join(os.getcwd(), IMAGE_DIR, self.dt)
        os.makedirs(img_dir, exist_ok=True)
        return img_dir

    def main(self):
        self.logger.info('start')
        self._execute()
        sleep(self.interval)
        while True:
            self._execute()
            if datetime.now() >= self.end:
                break
            sleep(self.interval)
        self.gdrive.upload(self.img_dir)
        self.logger.info('end')

    def _execute(self):
        pixels = self._make_pixels()
        if self.report:
            return
        self._save_image(pixels)
        self.remo.update(pixels)

    def _make_pixels(self):

        def _map(x, in_min, in_max, out_min, out_max):
            return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

        # get sensor readings
        pixels = self.sensor.readPixels()
        m = 'Min Pixel = {} C Max Pixel = {} C Thermistor = {} C'
        self.logger.debug(m.format(min(pixels), max(pixels), self.sensor.readThermistor()))

        # map sensor readings to color map
        MINTEMP = min(pixels) if self.min is None else self.min
        MAXTEMP = max(pixels) if self.max is None else self.max
        pixels = [_map(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]
        return pixels

    def _save_image(self, pixels):

        def _constrain(val, min_val, max_val):
            return min(max_val, max(min_val, val))

        # output image buffer
        image = Image.new('RGB', (NX, NY), 'white')
        draw = ImageDraw.Draw(image)
        # create the image
        for ix in range(NX):
            for iy in range(NY):
                draw.point([(ix, iy % NX)], fill=self.colors[_constrain(int(pixels[ix + NX * iy]), 0, COLORDEPTH - 1)])
        save_path = os.path.join(self.img_dir, '{0:%H:%M:%S}.jpg'.format(datetime.now()))
        # scale and save
        image.resize((NX * self.scale, NY * self.scale), Image.BICUBIC).save(save_path)
        self.logger.info('save image {}'.format(save_path))


if __name__ == '__main__':
    Thermal(COF_NAME).main()
