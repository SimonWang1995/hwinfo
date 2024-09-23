import os
import re
import sys
import logging
from utils import exec_command, dmidecode_parser
from prettytable import PrettyTable
from std_info import StdInfo
from collections import OrderedDict


class GPUInfo(StdInfo):
    def __init__(self):
        self.name = "GPU Information"
        self.log = logging.getLogger('hwinfo.gpu')
        self._gpus = []
        self.gpuinfo = []

    def parse(self):
        self.log.info('#gpu information')
        gpuinfo = NVGPU()
        if gpuinfo.probe():
            self.gpuinfo = gpuinfo.details()
        else:
            self.log.info("Not Found GPU")

    def get_details(self):
        return self.gpuinfo
        '''lspci 
        nvidia-smi -q
        lspci | grep -i nvidia 
        nvidia-smi -q 2>/dev/null | grep 'Product Name'
        nvidia-smi -q 2>/dev/null | grep 'Serial Number'
        nvidia-smi -q 2>/dev/null | grep 'Product Brand'
        nvidia-smi -q 2>/dev/null | grep 'GPU Part Number'
        nvidia-smi -q 2>/dev/null | grep 'VBIOS Version'
        ./tool/nvflash --version | grep 'Graphics Device'
        lspci 2>/dev/null | grep -i nvidia | grep -v -i bridge
        
        lspci -s 0e:00.0 -vvv 2>/dev/null|grep LnkSta:
            [2024-08-14 14:09:08,338][SYSINFO][INFO]cmd ret:
		    LnkSta:	Speed 32GT/s (ok), Width x16 (ok)

        [2024-08-14 14:09:08,412][SYSINFO][INFO]model:gpu,info:
{'GPU#1': {'FW': '96.00.99.00.1D',
           'LinkSpeed': '32GT/s(ok)',
           'PartNumber': '2329-846-A1',
           'ProductName': 'NVIDIA H20',
           'SLOT': '0e:00.0',
           'SN': '1652424079415',
           'VENDOR': 'NVIDIA',
           'Width': 'x16(ok)'},
 'GPU#2': {'FW': '96.00.99.00.1D',
           'LinkSpeed': '32GT/s(ok)',
           'PartNumber': '2329-846-A1',
           'ProductName': 'NVIDIA H20',
           'SLOT': '44:00.0',
           'SN': '1652424078659',
           'VENDOR': 'NVIDIA',
           'Width': 'x16(ok)'},
 'GPU#3': {'FW': '96.00.99.00.1D',
           'LinkSpeed': '32GT/s(ok)',
           'PartNumber': '2329-846-A1',
           'ProductName': 'NVIDIA H20',
           'SLOT': '4d:00.0',
           'SN': '1652524023336',
           'VENDOR': 'NVIDIA',
           'Width': 'x16(ok)'},
 'GPU#4': {'FW': '96.00.99.00.1D',
           'LinkSpeed': '32GT/s(ok)',
           'PartNumber': '2329-846-A1',
           'ProductName': 'NVIDIA H20',
           'SLOT': '58:00.0',
           'SN': '1652424078633',
           'VENDOR': 'NVIDIA',
           'Width': 'x16(ok)'},
 'GPU#5': {'FW': '96.00.99.00.1D',
           'LinkSpeed': '32GT/s(ok)',
           'PartNumber': '2329-846-A1',
           'ProductName': 'NVIDIA H20',
           'SLOT': '91:00.0',
           'SN': '1652524023051',
           'VENDOR': 'NVIDIA',
           'Width': 'x16(ok)'},
 'GPU#6': {'FW': '96.00.99.00.1D',
           'LinkSpeed': '32GT/s(ok)',
           'PartNumber': '2329-846-A1',
           'ProductName': 'NVIDIA H20',
           'SLOT': 'c1:00.0',
           'SN': '1652524023098',
           'VENDOR': 'NVIDIA',
           'Width': 'x16(ok)'},
 'GPU#7': {'FW': '96.00.99.00.1D',
           'LinkSpeed': '32GT/s(ok)',
           'PartNumber': '2329-846-A1',
           'ProductName': 'NVIDIA H20',
           'SLOT': 'ca:00.0',
           'SN': '1652524058674',
           'VENDOR': 'NVIDIA',
           'Width': 'x16(ok)'},
 'GPU#8': {'FW': '96.00.99.00.1D',
           'LinkSpeed': '32GT/s(ok)',
           'PartNumber': '2329-846-A1',
           'ProductName': 'NVIDIA H20',
           'SLOT': 'd5:00.0',
           'SN': '1652524057096',
           'VENDOR': 'NVIDIA',
           'Width': 'x16(ok)'}}
        '''

    def show_details(self):
        if self.gpuinfo:
            table = PrettyTable()
            table.title = self.name
            table.field_names = list(self.gpuinfo[0].keys())
            for gpu in self.gpuinfo:
                table.add_row(gpu.values())
            self.log.info('\n'+ str(table))


class NVGPU(object):
    def __init__(self) -> None:
        pass
        
    def probe(self):
        return self.has_gpu()

    def has_gpu(self):
        lspci_raw = os.popen('lspci').readlines()
        lsi_pci = re.compile('.*controller: NVIDIA*')
        for line in lspci_raw:
            if lsi_pci.search(line):
                return True
        return False

    def details(self):
        card_count = 0
        gpu_names = list()
        gpu_firmwares = list()
        gpu_pns = list()
        gpu_sns = list()
        gpu_bus_list = list()
        gpu_bus_widths = list()
        gpu_bus_speeds = list()
        adapters = list()
        lspci_info = exec_command('lspci')
        gpu_bus_list = re.findall("(.*?) .*? controller: NVIDIA*", lspci_info)
        card_count = len(gpu_bus_list)
        for bus in gpu_bus_list:
            lspci_vvv = exec_command('lspci -s {0} -vvv'.format(bus))
            lnksta = re.search("LnkSta:\sSpeed\s(.*?),\sWidth\s(.*?)[\n,]", lspci_vvv).groups()
            gpu_bus_widths.append(lnksta[1])
            gpu_bus_speeds.append(lnksta[0])
        nvsmi_loc = os.popen('which nvidia-smi 2>/dev/null')
        if nvsmi_loc.read():
            arg = nvsmi_loc.read().strip()
        else:
            raise FileNotFoundError('nvidia-smi command no\'t found')
        nvsmi_info = exec_command('nvidia-smi -q')
        gpu_names = re.findall("Product Name \s+: (.*?)\n", nvsmi_info)
        gpu_pns = re.findall("GPU Part Number \s+: (.*?)\n", nvsmi_info)
        gpu_sns = re.findall("Serial Number \s+: (.*?)\n", nvsmi_info)
        gpu_brands = re.findall("Product Brand \s+: (.*?)\n", nvsmi_info)
        gpu_vbios_list = re.findall("VBIOS Version \s+: (.*?)\n", nvsmi_info)
        # nvflash_info = exec_command("./tool/nvflash --version | grep 'Graphics Device'")
        for index in range(len(gpu_bus_list)):
            bus_id = gpu_bus_list[index]
            productname = gpu_names[index]
            pn = gpu_pns[index]
            sn = gpu_sns[index]
            vbios = gpu_vbios_list[index]
            brand = gpu_brands[index]
            width = gpu_bus_widths[index]
            speed = gpu_bus_speeds[index]
            adapters.append({'ID': index,
                             'Slot': bus_id,
                            'ProductName': productname,
                            'Part Number': pn,
                            'Serial Number': sn,
                            'FW': vbios,
                            'Width': width,
                            'Speed': speed})
        return adapters


if __name__ == '__main__':
    import json
    from utils import log_to_file
    log_to_file('log/gpu_info.log')
    gpu = GPUInfo()
    # if hba.supported():
    gpu.parse()
    print(json.dumps(gpu.get_details(), indent=4))
    gpu.show_details()
    # raid = RaidInfo()
