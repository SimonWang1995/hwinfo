import os
import sys
import logging
from utils import exec_command, dmidecode_parser
from prettytable import PrettyTable
from std_info import StdInfo
from collections import OrderedDict


def get_model_name():
    res_str = exec_command('ipmitool raw 6 1')
    res_str = (res_str[31:33]+res_str[28:30]).lower()

    if res_str == '007a':
        return True, 'ARBOK'
    elif res_str == '0075':
        return True, 'KINGLER' 
    elif res_str == '0081':
        return True, 'ENTEI'   
    elif res_str == '008d':
        return True, "STEELIX"
    else:
        return False, 'unsupported model'