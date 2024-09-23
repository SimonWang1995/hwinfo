import os
import sys
import logging
from utils import exec_command, dmidecode_parser
from prettytable import PrettyTable
from std_info import StdInfo
from collections import OrderedDict


class InfoTemplate(object):
    def parse(self):
        raise NotImplementedError


class MachineInfoTemplate(InfoTemplate):
    def __init__(self):
        self.ret = OrderedDict()
        self.Manufacturer = None
        self.Model = None
        self.ProductNumber = None
        self.SerialNumber = None
        self.Suite = None
        self.Assettag = None

    def parse(self):
        self.ret["Manufacturer"] = self.Manufacturer
        self.ret["Model"] = self.Model
        self.ret["ProductNumber"] = self.ProductNumber
        self.ret["SerialNumber"] = self.SerialNumber
        self.ret["Suite"] = self.Suite
        self.ret["Assettag"] = self.Assettag
        self.ret["TotalThreads"] = self.ThreadCount
        # self.ret["L3CacheKiB"] = self.L3CacheKiB
        return self.ret


class Machine(StdInfo):
    """
    Get the michine information, and check it is vm or not.
    """
    def __init__(self):
        self.name = 'server Information'
        self.machineinfo = OrderedDict()
        self.log = logging.getLogger('hwinfo.server')
        self.Manufacturer = 'NULL'
        self.Model = 'NULL'
        self.ProductNumber = None
        self.SerialNumber = None
        self.Suite = None
        self.Assettag = None

    def parse(self):
        self.log.info('#server information')
        info = exec_command('ipmitool fru print 0')
        fru0 = self._parser(info, ':')
        self.Manufacturer = fru0.get("Product Manufacturer", 'null')
        self.Model = fru0.get('Product Name', 'null')
        self.ProductNumber = fru0.get('Product Part Number')
        self.SerialNumber = fru0.get("Product Serial")
        try:
            self.Suite = fru0.get("Product Extra").split(':')[1]
        except Exception as e:
            pass
        self.Assettag = fru0.get("Product Asset Tag", 'null')

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
        self.machineinfo["Manufacturer"] = self.Manufacturer
        self.machineinfo["Model"] = self.Model
        self.machineinfo["ProductNumber"] = self.ProductNumber
        self.machineinfo["SerialNumber"] = self.SerialNumber
        self.machineinfo["Suite"] = self.Suite
        self.machineinfo["Assettag"] = self.Assettag
        # self.ret["L3CacheKiB"] = self.L3CacheKiB
        return self.machineinfo

    def show_details(self):
        table = PrettyTable()
        table.title = self.name
        table.field_names = list(self.machineinfo.keys())
        table.add_row(self.machineinfo.values())
        self.log.info('\n'+ str(table))

    def __repo__(self, manu, model, sn):
        print('MachineInfo: Manu#%s;Model#%s;SN#%s' % (manu, model, sn))


if __name__ == '__main__':
    import json
    from utils import log_to_file
    log_to_file('log/machine_info.log')
    machine = Machine()
    machine.parse()
    print(json.dumps(machine.get_details(), indent=4))
    machine.show_details()