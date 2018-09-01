import os
import sys
import yaml

from glob import glob
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

GAUTH = GoogleAuth()
DRIVE = GoogleDrive(GAUTH)

def uploadfiles(img_dir):

    with open('link.yaml', "r") as f:
        data = yaml.load(f)
    upload_files_path = glob(os.path.join(img_dir, '*.jpg'))
    if not upload_files_path:
        print('File does not exist. It does not upload.')
        sys.exit()

    for upload_file_path in upload_files_path:
        fname = '-'.join(upload_file_path.split('/')[-2:])
        print('Upload file:' + fname)
        img = DRIVE.CreateFile({"parents": [{"kind": "drive#fileLink", "id": data['link']}]})
        img.SetContentFile(upload_file_path)
        img['title'] = fname
        img.Upload()
