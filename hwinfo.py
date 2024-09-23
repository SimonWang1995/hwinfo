import os
import sys
import argparse
import logging
import json
from utils import log_to_file, logger_add_stream
from machine import Machine
from mlb_info import MlbInfo
from cpu_info import CpuInfo
from dram_info import DramInfo
from nic_info import NICInfo
from raidhba_info import HbaInfo
from psu_info import PSUInfo
from gpu_info import GPUInfo
from harddisk_info import SSDQuerier, HDDQuerier, NVMeQuerier

__Version__ = 'v0.01'
__auther__ = 'Simon.Wang'
__email__ = 'Wang.Simon@inventec.com.cn'
__date__ = '20240903'


SupportClass = ["server", "mlb", "cpu", 
                "mem", "psu", "raid", 
                "net", "hdd", "ssd", 
                "nvme", 'gpu']

check_item = {"server": Machine(), 
                    "mlb": MlbInfo(),
                    "cpu": CpuInfo(), 
                    "mem": DramInfo(), 
                    # "fwInfo": FwConf(), 
                    # "biosInfo": BiosConf(), 
                    "psu": PSUInfo(), 
                    "raid": HbaInfo(),
                    "net": NICInfo(),
                    # "bmcInfo": BmcConf(),

                    "hdd": HDDQuerier(), 
                    "ssd": SSDQuerier(),
                    "nvme": NVMeQuerier(),
                    "gpu": GPUInfo()}


class HardWareInfo(object):
    def __init__(self):
        filename = os.path.basename(__file__)
        filename = os.path.splitext(filename)
        self.check_item = check_item
        self.log = logging.getLogger('hwinfo')
        self.log.info("#HardWare Info")

    def parse(self):
        for name, mod in self.check_item.items():
            mod.parse()


    def get_all_info(self):
        value = {}
        for name, mod in self.check_item.items():
            res = mod.get_details()
            if name in ['server', 'mlb']:
                value.update(res)
            else:
                value.update({name: res})
        string_value = json.dumps(value, indent=4)
        self.log.info('%s' % string_value)
        return value
    
    def show_all_info(self):
        for name, mod in self.check_item.items():
            mod.show_details()

    def output(self):
        pass
    # def get_fw_versions(self):
    #     storage = ''
    #     nic = ''
    #     fw_dict = {}
    #     fw = FwVerService()
    #     storage = fw.get_storage_fw()
    #     if storage:
    #         fw_dict.update({'storage': storage})
    #     nic = fw.get_nic_fw()
    #     if nic:
    #         fw_dict.update({'nic': nic})
    #     dongle = fw.get_dongle_fw()
    #     if dongle:
    #         fw_dict.update({'dongle': dongle})
    #     psu = fw.get_psu_fw()
    #     if psu:
    #         fw_dict.update({'psu': psu})
    #     return fw_dict

    # def get_fw_attributes(self):
    #     hba = ''
    #     bmc = ''
    #     bios = ''
    #     nvram = ''
    #     pxe = ''
    #     fw_ver = ''
    #     value = {}
    #     hba = self.get_hba()
    #     if hba:
    #         value.update({'hba': hba})
    #     bmc = self.get_bmc()
    #     if bmc:
    #         value.update({'bmc': bmc})
    #     bios_attr, nvram_attr = self.get_bios()
    #     if bios_attr:
    #         value.update({'bios': bios_attr})
    #     if nvram_attr:
    #         value.update({'nvram': nvram_attr})
    #     pxe = self.get_pxe()
    #     if pxe:
    #         value.update({'pxe': pxe})
    #     fw_var = self.get_fw_versions()
    #     if fw_var:
    #         value.update(fw_var)
    #     string_value = json.dumps(value)
    #     self.log.info('%s' % string_value)
    #     return value


def parser_args():
    parser = argparse.ArgumentParser(prog='hwinfo', description='', usage="%(prog)s [-format] [-options ...]")
    parser.add_argument("-V", '-v', action='version', version=__Version__, help="show program's version number and exit")
    format_parser = parser.add_argument_group(description='format can be', prefix_chars='-')
    format_parser = format_parser.add_mutually_exclusive_group()
    format_parser.add_argument('-json', action='store_true', default=False, help="output hardware tree as a JSON object")
    format_parser.add_argument('-txt', action='store_true', default=False, help="output hardware tree as txt")
    options_parser = parser.add_argument_group(description='opions can be', prefix_chars='-')
    options_parser.add_argument('-class', dest='items', nargs='+', choices=SupportClass, help='only show a certain class of hardware')
    options_parser.add_argument('-log', help='set script output log to file')
    options_parser.add_argument('-quiet', action='store_true', default=False, help="don't display status")
    options_parser.add_argument('-dump', help="save hardware tree to a file")
    return parser.parse_args()


def setup_logger(LogFile):
    """Setup logging configuration. Options gets altered here. Because ghetto.
    
    :param options: Options from parse_args. Should include tag array.
    :type options: namespace
    
    """
    LogPath = os.path.dirname(os.path.abspath(LogFile))
    filename = os.path.basename(LogFile)
    os.makedirs(LogPath, exist_ok=True)
    # filename = __file__.split('/')[-1].strip('.pyc').strip('.py')
    # log_to_file(os.path.join(LogPath, filename+'.log'))
    log_to_file(os.path.join(LogPath, filename))


def get_items(items):
    value = {}  
    for item in items:
        mod = check_item[item]
        mod.parse()
        res = mod.get_details()
        value.update({item: res})
    string_value = json.dumps(value, indent=4)
    log.info('%s' % string_value)
    return value


def show_items(items):
    for item in items:
        log.info("="*80)
        mod = check_item[item]
        mod.parse()
        res = mod.get_details()
        mod.show_details()
        log.info('')


if __name__ == '__main__':
    log = logging.getLogger('hwinfo')
    args = parser_args()
    jsonflag = args.json
    txtflag = args.txt
    sitem = SupportClass
    filename = args.dump
    quiet = args.quiet
    if args.log:
        setup_logger(args.log)
    if args.items:
        sitem = args.items
    log.info('args:' + str(args))
    log.info('command: ' + ' '.join(sys.argv[:]))
    if not quiet:
        logger_add_stream()
    if jsonflag:
        res = get_items(sitem)
        print(json.dumps(res, indent=4))
        if filename:
            json.dump(res, open(filename, 'w'), indent=4)
    else:
        show_items(sitem)



    # setup_logger('log')
    # hwinfo = HardWareInfo()
    # hwinfo.parse()
    # info = hwinfo.get_all_info()
    # print(json.dumps(info, indent=4))
    # hwinfo.show_all_info()