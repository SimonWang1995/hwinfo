import os
import sys
import logging
from utils import exec_command, dmidecode_parser
from collections import OrderedDict


class StdInfo(object):
    def __init__(self):
        self.name = 'std_info'
        self.log = logging.getLogger('hwinfo.std')
        # self.log = None

    def get_details(self):
        raise NotImplementedError()

    def title(self):
        self.log.info('-'*70)
        self.log.info(self.name.center(70, ' '))
        self.log.info('-'*70)

    def output(self):
        raise NotImplementedError()

    def end_log(self):
        self.log.info('-'*70)