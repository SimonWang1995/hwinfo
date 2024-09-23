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


class CpuInfoTemplate(InfoTemplate):
    def __init__(self):
        self.ret = OrderedDict()
        self.Socket = None
        self.Manufacturer = None
        self.Model = None
        self.Id = None
        self.MaxSpeed = None
        self.CurrentSpeed = None
        self.CoreCount = None
        self.ThreadCount = None
        self.L3CacheKiB = None

    def parse(self):
        self.ret["Socket"] = self.Socket
        self.ret["Manufacturer"] = self.Manufacturer
        self.ret["Model"] = self.Model
        self.ret["PPIN"] = self.Id
        self.ret["MaxSpeedMHz"] = self.MaxSpeed
        self.ret["CurrentSpeedMHz"] = self.CurrentSpeed
        self.ret["TotalCores"] = self.CoreCount
        self.ret["TotalThreads"] = self.ThreadCount
        # self.ret["L3CacheKiB"] = self.L3CacheKiB
        return self.ret


class CpuInfo(StdInfo):
    def __init__(self):
        self.name = 'CPU Information'
        self.cpuinfo = OrderedDict()
        self._cpus = list()
        self.cpuslot = []
        self.cpumodel = []
        self.Maximum = 0
        self.log = logging.getLogger('hwinfo.cpu')

    def parse(self):
        """Get cpu information"""
        self.log.info('#cpu information')
        command = "dmidecode -t 4"
        dmitype4 = exec_command(command)
        cpuinfo_list = dmidecode_parser(dmitype4)
        for cpuinfo in cpuinfo_list:
            cpu = CpuInfoTemplate()
            cpu.Socket = cpuinfo.get("Socket Designation")
            if 'CPU' in cpu.Socket:
                self.Maximum += 1
            cpu.Manufacturer = cpuinfo.get("Manufacturer")
            cpu.Model = cpuinfo.get("Version")
            # cpu.Microcode = self.microcode
            cpu.MaxSpeed = cpuinfo.get("Max Speed")
            cpu.CurrentSpeed = cpuinfo.get("Current Speed")
            cpu.CoreCount = cpuinfo.get("Core Count")
            cpu.ThreadCount = cpuinfo.get("Thread Count")
            cpu.Id = cpuinfo.get("ID").replace(" ", "")
            # cpu.L3CacheKiB = self.cache
            self._cpus.append(cpu)
    
    def get_details(self):
        self.cpuinfo['Maximum'] = self.Maximum
        tmp = []
        for cpu in self._cpus:
            tmp.append(cpu.parse())
        self.cpuinfo['details'] = tmp
        return self.cpuinfo
    
    def output(self):
        for cpu in self._cpus:
            cpuinfo = cpu.parse()
            self.log.info(cpuinfo['Socket'].center(50, '*'))
            for name, value in cpuinfo.items():
                self.log.info("{0:20} : {1}".format(name, value))

    def show_details(self):
        table = PrettyTable()
        table.title = self.name
        for cpu in self._cpus:
            cpuinfo = cpu.parse()
            table.field_names = cpuinfo.keys()
        # for cpu in self.cpuinfo['details']:
            table.add_row(cpuinfo.values())
        self.log.info('\n'+ str(table))
        return table


if __name__ == '__main__':
    import json
    from utils import log_to_file
    log_to_file('log/cpu_info.log')
    cpu = CpuInfo()
    cpu.parse()
    print(json.dumps(cpu.get_details(), indent=4))
    cpu.title()
    cpu.output()
    cpu.end_log()
    cpu.show_details()