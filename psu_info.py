import os
import re
import sys
import glob
import logging
from prettytable import PrettyTable
from collections import OrderedDict
from std_info import StdInfo
from utils import exec_command, dmidecode_parser


class InfoTemplate(object):
    def parse(self):
        raise NotImplementedError


class PsuInfoTemplate(InfoTemplate):
    def __init__(self):
        self.ret = OrderedDict()
        self.Location = None
        self.Manufacturer = None
        self.Model = None
        self.SerialNumber = None
        self.Firmware = None
        self.MaxPower = None

    def parse(self):
        self.ret["Location"] = self.Location
        self.ret["Manufacturer"] = self.Manufacturer
        self.ret["Model"] = self.Model
        self.ret['SerialNumber'] = self.SerialNumber
        self.ret["Firmware"] = self.Firmware
        self.ret["MaxPower"] = self.MaxPower
        return self.ret


class PSUInfo(StdInfo):
    def __init__(self):
        self.name = 'PSU Information'
        self.Maximum = 0
        self._psus = []
        self.psuinfo = []
        self.log = logging.getLogger('hwinfo.psu')

    def parse(self):
        """Get PSU information"""
        self.log.info('#psu information')
        command = "ipmitool fru print "
        fru_info = exec_command(command)
        fru_list = re.findall("(FRU Device.*?)\n\n", fru_info, re.M | re.S)
        for fruinfo in fru_list:
            if 'PSU' in fruinfo:
                psufru = self._parser_fru(fruinfo)
                psu = PsuInfoTemplate()
                psu.Location = re.search('(PSU[0-9])', psufru['FRU Device Description']).group()
                psu.Manufacturer = psufru.get('Product Manufacturer')
                psu.Model= psufru.get('Product Name')
                psu.SerialNumber = psufru.get('Product Serial', 'null')
                psu.Firmware = psufru.get('Product Version','null')
                psu.MaxPower = psufru.get('Product Asset Tag', 'null')
                self.Maximum += 1
                self._psus.append(psu)

    def get_details(self):
        """Get PSU information"""
        # self.cpuinfo['Maximum'] = self.Maximum
        # tmp = []
        for psu in self._psus:
            self.psuinfo.append(psu.parse())
        return self.psuinfo
    
    # def get_details(self):
    #     """Get PSU information"""
    #     self.psuinfo['Maximum'] = self.Maximum
    #     tmp = []
    #     for psu in self._psus:
    #         tmp.append(psu.parse())
    #     self.psuinfo['details'] = tmp
    #     return self.psuinfo

    def _parser_fru(self, fru):
        # key = fru.split('\n')[0].split(':')[1]
        fru_dict = OrderedDict()
        for line in fru.split('\n'):
            if ':' in line:
                parts = line.split(':')
                name = parts[0].strip()
                fru_dict[parts[0].strip()] = parts[1].strip()
        return fru_dict

    def output(self):
        pass

    def show_details(self):
        if self._psus:
            table = PrettyTable()
            table.title = self.name
            table.field_names = self._psus[0].parse().keys()
            for psu in self._psus:
                table.add_row(psu.parse().values())
            self.log.info('\n'+ str(table))


if __name__ == '__main__':
    import json
    from utils import log_to_file
    log_to_file('log/psu_info.log')
    psu = PSUInfo()
    psu.parse()
    print(json.dumps(psu.get_details(), indent=4))
    psu.show_details()