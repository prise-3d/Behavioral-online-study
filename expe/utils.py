# main imports
import os
import random
from datetime import datetime
import uuid
import json

# module imports
from . import config as cfg

def uniqueID():
    '''
    Return unique identifier for current user
    '''
    return str(uuid.uuid4())


def write_header_expe(f, expe_name):
    '''
    Write specific header into file
    '''

    f.write(cfg.expes_configuration[expe_name]['output_header'])


def merge_data(current, additionals):

    for k, v in additionals.items():
        current[k] = v

    return current

def update_json_file(filepath, data):
    
    metadata = {}

    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    
    # set new data values
    for k, v in data.items():
        metadata[k] = v

    # save expected metadata
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
        