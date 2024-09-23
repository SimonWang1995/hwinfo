import os
import sys
import re
import logging
from collections import OrderedDict
from utils import exec_command, dmidecode_parser
from std_info import StdInfo
from prettytable import PrettyTable


class MemoryInfoTemplate(object):
    def __init__(self):
        self.Location = None
        self.Manufacturer = None
        self.Capacity = None
        self.OperatingSpeed = None
        self.SerialNumber = None
        self.PartNumber = None
        self.RatedSpeed = None
        self.MemoryDeviceType = None
        self.RankCount = None
        # self.MinVoltageMillivolt = None

    def parse(self):
        ret = OrderedDict()
        ret["Location"] = self.Location
        ret["Manufacturer"] = self.Manufacturer
        ret["PartNumber"] = self.PartNumber
        ret["SerialNumber"] = self.SerialNumber
        ret["Capacity"] = self.Capacity
        ret["OperatingSpeed"] = self.OperatingSpeed
        ret["RatedSpeed"] = self.RatedSpeed
        ret["DeviceType"] = self.MemoryDeviceType
        ret["RankCount"] = self.RankCount
        # ret["MinVoltageMillivolt"] = self.MinVoltageMillivolt
        return ret



class DramInfo(StdInfo):
    def __init__(self):
        self.name = 'DIMM Information'
        self.log = logging.getLogger('hwinfo.dram')
        self.Maximum = 0
        # self.dimmnumber = 0
        self.TotalSystemMemoryGiB = 0
        self.meminfo = OrderedDict()
        self. _Mem_topo = ''
        # self.presentDimmNames = []
        # self.goodmeminfo = []
        # self.badmeminfo = []
        self._dimms = []

    @property
    def mem_topo(self):
        return self._Mem_topo

    def parse(self):
        self.log.info('#dram information')
        command = "dmidecode -t 17"
        dmimsg = exec_command(command)
        memlist = dmidecode_parser(dmimsg)
        for meminfo in memlist:
            mem = MemoryInfoTemplate()
            mem.Location = meminfo.get('Locator')
            mem.Manufacturer = meminfo.get('Manufacturer')
            mem.PartNumber = meminfo.get('Part Number')
            mem.SerialNumber = meminfo.get('Serial Number')
            mem.Capacity = meminfo.get('Size')
            Size = re.search('\d+', mem.Capacity)
            mem.OperatingSpeed = meminfo.get('Configured Clock Speed')
            mem.RatedSpeed = meminfo.get('Speed')
            mem.MemoryDeviceType = meminfo.get('Type')
            mem.RankCount = meminfo.get('Rank')
            # mem.MinVoltageMillivolt = meminfo.get('Minimum Voltage')
            # self._dimms.append(mem)
            if Size:
                self.Maximum += 1
                self.TotalSystemMemoryGiB += int(Size.group(0))
                self._dimms.append(mem)
                self._Mem_topo += '1'
            else:
                self._Mem_topo += '0'

    def get_details(self):
        self.meminfo['Maximum'] = self.Maximum
        self.meminfo['DRAM_TOP'] = self.mem_topo
        self.meminfo['TotalSystemMemorySize[GiB]'] = self.TotalSystemMemoryGiB
        self.meminfo['details'] = []
        for dimm in self._dimms:
            self.meminfo['details'].append(dimm.parse())
        return self.meminfo
    
    def show_details(self):
        table = PrettyTable()
        table.title = self.name
        for dimm in self._dimms:
            dimminfo = dimm.parse()
            table.field_names = dimminfo.keys()
        # for mem in self.meminfo['details']:
            table.add_row(dimminfo.values())
        self.log.info('\n'+ str(table))
        return table
    

if __name__ == '__main__':
    import json
    from utils import log_to_file
    log_to_file('log/dram_info.log')
    dram = DramInfo()
    dram.parse()
    print(json.dumps(dram.get_details(), indent=4))
    # dram.title()
    dram.show_details()
    # dram.end_log()