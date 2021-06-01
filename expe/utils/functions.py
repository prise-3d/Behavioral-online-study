# main imports
import random
from datetime import datetime
import uuid

# module imports
from .. import config as cfg

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