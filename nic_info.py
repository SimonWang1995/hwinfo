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


class NicInfoTemplate(InfoTemplate):
    def __init__(self):
        self.ret = OrderedDict()
        self.Bus = None
        self.Manufacturer = None
        self.Model = None
        self.PartNumber = None
        self.SerialNumber = None
        self.Firmware = None
        self.PortCount = None
        self.port_templates = []

    def get_port_info_template(self):
        port_info = NicPortInfoTemplate()
        self.port_templates.append(port_info)
        return port_info

    def parse(self):
        self.ret["Bus"] = self.Bus
        self.ret["Manufacturer"] = self.Manufacturer
        self.ret['Model'] = self.Model
        self.ret["PartNumber"] = self.PartNumber
        self.ret['Serialnumber'] = self.SerialNumber
        self.ret["Firmware"] = self.Firmware
        self.ret["PortCount"] = self.PortCount
        tmp = []
        for port in self.port_templates:
            tmp.append(port.parse())
        return self.ret
    
    def parse_port(self):
        tmp = []
        for port in self.port_templates:
            tmp.append(port.parse())
        return tmp


class NicInfoTemplate_New(InfoTemplate):
    def __init__(self):
        self.ret = OrderedDict()
        self.ctl = OrderedDict()
        self.Bus = None
        self.DEVID = None
        self.SYSID = None
        self.Manufacturer = None
        self.LinkSpeed = None
        self.LinkWidth = None
        self.Model = None
        self.Type = None
        self.PartNumber = None
        self.SerialNumber = None
        self.Firmware = None
        self.Mac = None
        self.Speed = None
        self.port_templates = NicPortInfoTemplate()

    def get_port_info_template(self):
        port_info = NicPortInfoTemplate()
        self.port_templates.append(port_info)
        return port_info

    def parse(self):
        self.ret["Bus"] = self.Bus
        self.ret['DEVID'] = self.DEVID
        self.ret['SYSID'] = self.SYSID
        self.ret["Manufacturer"] = self.Manufacturer
        self.ret['Model'] = self.Model
        self.ret['Type'] = self.Type
        self.ret["PartNumber"] = self.PartNumber
        self.ret['Serialnumber'] = self.SerialNumber
        self.ret["Firmware"] = self.Firmware
        self.ret['LinkSpeed'] = self.LinkSpeed
        self.ret['LinkWidth'] = self.LinkWidth
        self.ret['Port'] = self.port_templates.parse()
        return self.ret
    
    def parse_port(self):
        return self.port_templates.parse()
    
    def parse_controler(self):
        self.ctl["Bus"] = self.Bus
        # self.ctl['DEVID'] = self.DEVID
        # self.ctl['SYSID'] = self.SYSID
        self.ctl["Manufacturer"] = self.Manufacturer
        self.ctl['Model'] = self.Model
        self.ctl['Type'] = self.Type
        self.ctl["PartNumber"] = self.PartNumber
        self.ctl['Serialnumber'] = self.SerialNumber
        self.ctl["Firmware"] = self.Firmware
        self.ctl['LinkSpeed'] = self.LinkSpeed
        self.ctl['LinkWidth'] = self.LinkWidth
        # self.ctl['MacAddr'] = self.Mac
        # self.ctl['Speed'] = self.Speed
        return self.ctl


class NicPortInfoTemplate(InfoTemplate):
    def __init__(self):
        self.ret = OrderedDict()
        self.ID = None
        self.PortName = None
        self.MacAddr = None
        self.DriverVersion = None
        self.Driver = None
        self.Speed = None
        self.MediaType = None
        self.LinkStatus = None

    def parse(self):
        self.ret["ID"] = self.ID
        self.ret["PortName"] = self.PortName
        self.ret["MacAddr"] = self.MacAddr
        self.ret['Speed'] = self.Speed
        self.ret['Driver'] = self.Driver
        self.ret['DriverVersion'] = self.DriverVersion
        self.ret["MediaType"] = self.MediaType
        self.ret["LinkStatus"] = self.LinkStatus
        return self.ret


class NICInfo(StdInfo):
    desc = 'Ethernet'
    _lspci_mr_command = 'lspci -vmm -s %s'
    _lspci_vvvn_command = 'lspci -vvvn -s %s'
    _lspci_verbose_command = 'lspci -v -s %s'
    _lspci_vverbose_command = 'lspci -vv -s %s'
    def __init__(self):
        self.name = 'Ethernet Information'
        self.log = logging.getLogger('hwinfo.nic')
        self.Maximum = 0
        self._nics = []
        self.all_interface = []
        self.ctrinfo = []
        self.portinfo = []
        self.nicinfo = []

    def get_interfaces(self):
        for interface in glob.glob("/sys/class/net/[ei]*"):
            self.all_interface.append(interface.split(os.sep)[-1])
        return self.all_interface
    
    def get_bus_id_list(self):
        command = "lspci | awk /Ethernet/'{print $1}'"
        buslist = exec_command(command).strip('\n')
        self.buslist = buslist.split('\n')
        return self.buslist
    
    def parse(self):
        self.log.info('#nic information')
        self.get_interfaces()
        self.get_bus_id_list()
        for interface in self.all_interface:
            nic = NicInfoTemplate_New()
            nicport = nic.port_templates
            nic_log = exec_command('ethtool -i ' + interface)
            nic_log1 = exec_command('ethtool ' + interface)
            nic_info = self._parser(nic_log, ':')
            nic_info1 = self._parser(nic_log1, ':')
            self.bus = nic_info.get('bus-info')
            nic.Bus = self.bus
            nicport.ID = self.bus
            nicport.PortName = interface
            nicport.Driver = nic_info.get('driver')
            nicport.DriverVersion = nic_info.get('version')
            nicport.Speed = nic_info1.get('Speed')
            nic.Speed = nicport.Speed
            nicport.LinkStatus = nic_info1['Link detected']
            nicport.MacAddr = os.popen('cat /sys/class/net/'+ interface+'/address').read().strip()
            nic.Mac = nicport.MacAddr
            nic.Firmware = nic_info.get('firmware-version')
            if re.search("\d{4}:[0-9a-z]{2}:[0-9a-z]{2}", self.bus):
                pci_mr_info = self._parser(exec_command(self._lspci_mr_command % self.bus), ':')
                nic.Manufacturer = pci_mr_info['Vendor'].split()[0]
                nic.Model = pci_mr_info['Device']
                vvvn = exec_command(self._lspci_vvvn_command % self.bus)
                nic.DEVID = vvvn.splitlines()[0].split()[2]
                nic.SYSID = re.search("Subsystem: (.*?)\n", vvvn).group(1)
                verbose = exec_command(self._lspci_vverbose_command % self.bus)
                PName = re.search('Product Name:(.*?)\n', verbose)
                lnksta_speed = re.search('LnkSta.*Speed (\d.*?GT/s)', verbose).group(1)
                lnksta_width = re.search('LnkSta.*Width (x\d+)', verbose).group(1)
                nic.LinkSpeed = lnksta_speed
                nic.LinkWidth = lnksta_width
                if PName:
                    PName = PName.group(1)
                    if 'OCP' in PName:
                        nic.Type = 'OCP'
                    else:
                        nic.Type = 'PCIe'
                PN = re.search('Part number:(.*?)\n', verbose)
                if PN:
                    nic.PartNumber = PN.group(1)
                SN = re.search('Serial number:(.*?)\n', verbose)
                if SN:
                    nic.SerialNumber = SN.group(1)
            else:
                nic.Type = 'USB'
            self._nics.append(nic)

    def _parser(self, info, split):
        # key = fru.split('\n')[0].split(':')[1]
        res = OrderedDict()
        for line in info.split('\n'):
            if ':' in line:
                parts = line.split(split, 1)
                name = parts[0].strip()
                res[parts[0].strip()] = parts[1].strip()
        return res
    
    def get_controler(self):
        for nic in self._nics:
            self.ctrinfo.append(nic.parse_controler())
        return self.ctrinfo
    
    def get_portinfo(self):
        for nic in self._nics:
            self.portinfo.append(nic.parse_port())
        return self.portinfo

    def parse_info(self):
        pass

    def _parse_busid(self, busid):
        pass

    def get_details(self):
        self.get_controler()
        self.get_portinfo()
        for nic in self._nics:
            self.nicinfo.append(nic.parse())
        return self.nicinfo

    def get_businfo(self):
        for nic in self._nics:
            self.businfo.append(nic.businfo)
        return self.businfo


    def __repr__(self):
        """Define a basic representation of the class object."""
        rep = '<NICList contents:\n'
        for device in self._nics:
            rep += str(device) + '\n'
        return rep + '>'

    def show_details(self):
        self.show_contrlerinfo()
        self.show_portinfo()

    def show_portinfo(self):
        if self.portinfo:
            table = PrettyTable()
            table.title = 'NICPort Information'
            table.field_names = list(self.portinfo[0].keys())
            for port in self.portinfo:
                table.add_row(port.values())
            self.log.info('\n'+ str(table))

    def show_contrlerinfo(self):
        if self.ctrinfo:
            table = PrettyTable()
            table.title = 'NIC Controler Information'
            table.field_names = list(self.ctrinfo[0].keys())
            for ctr in self.ctrinfo:
                table.add_row(ctr.values())
            self.log.info('\n'+ str(table))


if __name__ == '__main__':
    import json
    from utils import log_to_file
    log_to_file('log/nic_info.log')
    nic = NICInfo()
    nic.parse()
    print(json.dumps(nic.get_portinfo(), indent=4))
    print(json.dumps(nic.get_controler(), indent=4))
    print(json.dumps(nic.get_details(), indent=4))
    nic.show_portinfo()
    nic.show_contrlerinfo()
    # nic.show_details()
