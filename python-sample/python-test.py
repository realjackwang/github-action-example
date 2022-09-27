import json
from PIL import Image
import sys
import os
import requests
from obs import *
current_file_path = os.path.dirname(os.path.realpath(__file__))
# append current path to search paths, so that we can import some third party libraries.
sys.path.append(current_file_path)

TEMP_ROOT_PATH = "/tmp/"
secure = True
signature = 'v4'
port = 443
path_style = True

def newObsClient(context, obs_server):
    ak = context.getAccessKey()
    sk = context.getSecretKey()
    return ObsClient(access_key_id=ak, secret_access_key=sk, server=obs_server,
                     path_style=True, ssl_verify=False, max_retry_count=5, t
