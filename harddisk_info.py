import os
import re
import sys
import glob
import logging
from prettytable import PrettyTable
from collections import OrderedDict
from std_info import StdInfo
from utils import exec_command, dmidecode_parser
from device import Device, NVMe, discover_disks


class NVMeQuerier(StdInfo):
    """
    Get NVMe Card Information, including Model, SN, FW
    """
    _desc = 'NVMe'

    def __init__(self):
        self.Maximum = 0
        self._nvmes = []
        self.nvmeinfo = []
        self.nvmebaseinfo = []
        self.nvmesmartinfo = []
        self.name = 'NVMe Information'
        self.log = logging.getLogger('hwinfo.nvme')

    def discover(self):
        nvme_devices = glob.glob("/sys/class/nvme/nvme*")
        if nvme_devices:
            return [device.split('/')[-1] for device in nvme_devices]
        return nvme_devices

    def __repr__(self):
        """Define a basic representation of the class object."""
        rep = '<NVMeList contents:\n'
        for device in self._nvmes:
            rep += str(device) + '\n'
        return rep + '>'

    def parse(self):
        self.log.info("#nvme information")
        nvme_devices = self.discover()
        for nvme in nvme_devices:
            self._nvmes.append(NVMe(nvme))

    def get_baseinfo(self):
        for nvme in self._nvmes:
            self.nvmebaseinfo.append(nvme.get_baseinfo())
        return self.nvmebaseinfo.copy()
    
    def get_smartinfo(self):
        for nvme in self._nvmes:
            self.nvmesmartinfo.append(nvme.get_baseinfo())
        return self.nvmesmartinfo.copy()

    def get_details(self):
        for nvme in self._nvmes:
            self.nvmeinfo.append(nvme.as_dict())
        return self.nvmeinfo.copy()
    
    def show_details(self):
        if self._nvmes:
            table = PrettyTable()
            table.title = self.name
            table.field_names = list(self._nvmes[0].as_dict().keys())
            for nvme in self._nvmes:
                table.add_row(nvme.as_dict().values())
            self.log.info('\n'+ str(table))


class SSDQuerier(StdInfo):
    """
    Get NVMe Card Information, including Model, SN, FW
    """
    _desc = 'SSD'

    def __init__(self):
        self.Maximum = 0
        self.name = 'SSD Information'
        self._ssds = []
        self.ssdinfo = []
        self.log = logging.getLogger('hwinfo.ssd')

    def discover(self):
        return discover_disks()['SSD']

    def __repr__(self):
        """Define a basic representation of the class object."""
        rep = '<DeviceList contents:\n'
        for device in self._ssds:
            rep += str(device) + '\n'
        return rep + '>'

    def parse(self):
        self.log.info('#ssd information')
        ssdlist = self.discover()
        for ssd in ssdlist:
            self._ssds.append(Device(ssd))
            self.Maximum = len(self._ssds)

    def get_details(self):
        for device in self._ssds:
            self.ssdinfo.append(device.as_dict())
        return self.ssdinfo

    def show_details(self):
        if self._ssds:
            table = PrettyTable()
            table.title = self.name
            table.field_names = list(self._ssds[0].as_dict().keys())
            for ssd in self._ssds:
                table.add_row(ssd.as_dict().values())
            self.log.info('\n'+ str(table))


class HDDQuerier(object):
    """
    Get NVMe Card Information, including Model, SN, FW
    """
    _desc = 'HDD'

    def __init__(self):
        self.Maximum = 0
        self.hddnames = []
        self._hdds = []
        self.hddinfo = []
        self.name = 'HDD Information'
        self.log = logging.getLogger('hwinfo.hdd')

    def discover(self):
        return discover_disks()['HDD']

    def __repr__(self):
        """Define a basic representation of the class object."""
        rep = '<DeviceList contents:\n'
        for device in self._hdds:
            rep += str(device) + '\n'
        return rep + '>'

    def parse(self):
        self.log.info('#hdd information')
        self.hddnames = self.discover()
        for hdd in self.hddnames:
            self._hdds.append(Device(hdd))

    def get_details(self):
        for device in self._hdds:
            self.hddinfo.append(device.as_dict())
        return self.hddinfo
    
    def show_details(self):
        if self._hdds:
            table = PrettyTable()
            table.title = self.name
            table.field_names = list(self._hdds[0].as_dict().keys())
            for hdd in self._hdds:
                table.add_row(hdd.as_dict().values())
            self.log.info('\n'+ str(table))


if __name__ == '__main__':
    import json
    from utils import log_to_file
    log_to_file('log/harddisk_info.log')
    hdd = HDDQuerier()
    hdd.parse()
    print(json.dumps(hdd.get_details(), indent=4))
    hdd.show_details()
    ssd = SSDQuerier()
    ssd.parse()
    print(json.dumps(ssd.get_details(), indent=4))
    ssd.show_details()
    nvme = NVMeQuerier()
    nvme.parse()
    print(json.dumps(nvme.get_details(), indent=4))
    nvme.show_details()

