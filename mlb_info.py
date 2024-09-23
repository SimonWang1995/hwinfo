import os
import re
import sys
import logging
from utils import exec_command, dmidecode_parser
from prettytable import PrettyTable
from std_info import StdInfo
from collections import OrderedDict


class InfoTemplate(object):
    def parse(self):
        raise NotImplementedError


class MlbInfoTemplate(InfoTemplate):
    def __init__(self):
        self.ret = OrderedDict()
        self.BIOS = None
        self.BIOS_RELEASE = None
        self.BMC = None
        self.BMC_MAC = None
        self.CPLD = None
        self.EXTRA_PN = None
        self.PartNumber = None
        self.SerialNumber = None
        self.ProductName = None
        self.Version = None
        self.Manufacturer = None

    def parse(self):
        self.ret["BIOS"] = self.BIOS
        self.ret["BMC"] = self.BMC
        self.ret["BMC_MAC"] = self.BMC_MAC
        self.ret["CPLD"] = self.CPLD
        self.ret["PartNumber"] = self.PartNumber
        self.ret["ProductName"] = self.ProductName
        self.ret["SerialNumber"] = self.SerialNumber
        self.ret['Version'] = self.Version
        self.ret['Manufacturer'] = self.Manufacturer
        return self.ret


class MlbInfo(StdInfo):
    def __init__(self):
        super().__init__()
        self.name = 'MLB Information'
        self.log = logging.getLogger('hwinfo.mlb')
        self.MLBinfo = OrderedDict()
        self._mlb = MlbInfoTemplate()

    def parse(self):
        self.log.info("#MLB information")
        lan1 = exec_command('ipmitool lan print')
        self._mlb.BMC_MAC = re.search("MAC Address(\s*?): (.*?)\n", lan1).group(2)
        ret_res = exec_command('ipmitool raw 6 1').split()
        self._mlb.BMC = '.'.join(ret_res[2:4]) +'.' + ret_res[11]
        self._mlb.BIOS = exec_command('dmidecode -s bios-version').strip()
        fru0_info = exec_command('ipmitool fru print 0')
        dmi_t2 = exec_command('dmidecode -t 2')
        fru0 = self._parser(fru0_info, ':')
        dmi2 = dmidecode_parser(dmi_t2)[0]
        self._mlb.Manufacturer = dmi2.get('Manufacturer')
        self._mlb.ProductName = dmi2.get('Product Name')
        self._mlb.SerialNumber = dmi2.get("Serial Number")
        self._mlb.PartNumber = dmi2.get("Version")
        try:
            self._mlb.Version = fru0.get("Board Extra").split(':')[1]
        except Exception as e:
            pass
        self.MLBinfo = self._mlb.parse()


    def _parser(self, info, split):
        # key = fru.split('\n')[0].split(':')[1]
        res = OrderedDict()
        for line in info.split('\n'):
            if ':' in line:
                parts = line.split(split, 1)
                name = parts[0].strip()
                res[parts[0].strip()] = parts[1].strip()
        return res
    
    def get_details(self):
        return self.MLBinfo

    def show_details(self):
        table = PrettyTable()
        table.title = self.name
        table.field_names = list(self.MLBinfo.keys())
        table.add_row(self.MLBinfo.values())
        self.log.info('\n'+ str(table))


if __name__ == '__main__':
    import json
    from utils import log_to_file
    log_to_file('log/mlb_info.log')
    mlb = MlbInfo()
    mlb.parse()
    print(json.dumps(mlb.get_details(), indent=4))
    mlb.show_details()