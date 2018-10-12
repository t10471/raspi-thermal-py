import os
import logging
import yaml

from glob import glob
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class GDriveFactory:

    @staticmethod
    def create(config, fname):
        return GDrive(fname) if config['use_drive'] else DummyGDrive(fname)

class DummyGDrive:

    def __init__(self, fname):
        pass

    def upload(self, img_dir):
        pass

class GDrive:

    def __init__(self, fname):
        lg = logging.getLogger('googleapiclient')
        lg.setLevel(logging.CRITICAL)
        # lg.propagate = True
        self.logger = logging.getLogger('Thermal').getChild('Upload')
        self.drive = GoogleDrive(GoogleAuth())
        with open(fname, "r") as f:
            self.config = yaml.load(f)['drive']

    def upload(self, img_dir):
        upload_files_path = glob(os.path.join(img_dir, '*.jpg'))
        if not upload_files_path:
            self.logger.error('File does not exist. It does not upload.')

        for upload_file_path in upload_files_path:
            fname = '-'.join(upload_file_path.split('/')[-2:])[5:-7] + '.jpg'
            self.logger.info('Upload file:' + fname)
            img = self.drive.CreateFile({'parents': [{'kind': 'drive#fileLink',
                                                      'id': self.config['link']}]})
            img.SetContentFile(upload_file_path)
            img['title'] = fname
            img.Upload()
