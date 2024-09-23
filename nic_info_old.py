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
        self.Slot = None
        self.Manufacturer = None
        self.PartNumber = None
        self.Serialnumber = None
        self.Firmware = None
        self.PortCount = None

    def parse(self):
        self.ret["Slot"] = self.Slot
        self.ret["Manufacturer"] = self.Manufacturer
        self.ret["PartNumber"] = self.PartNumber
        self.ret['Serialnumber'] = self.Serialnumber
        self.ret["Firmware"] = self.Firmware
        self.ret["PortCount"] = self.PortCount
        return self.ret


class NicPortInfoTemplate(InfoTemplate):
    def __init__(self):
        self.ret = OrderedDict()
        self.ID = None
        self.PortName = None
        self.MacAddr = None
        self.Speed = None
        self.MediaType = None
        self.LinkStatus = None

    def parse(self):
        self.ret["ID"] = self.ID
        self.ret["PortName"] = self.PortName
        self.ret["MacAddr"] = self.MacAddr
        self.ret['Speed'] = self.Speed
        self.ret["MediaType"] = self.MediaType
        self.ret["LinkStatus"] = self.LinkStatus
        return self.ret


class NIC(object):
    def __init__(self, portname):
        self.portname = portname
        self.nicinfo = {}
        self.businfo = {}
        self.portinfo = {}
        self.parse()

    def parse(self):
        self.nic_log = os.popen('ethtool -i ' + self.portname).read()
        self.bus = re.search('bus-info: (.*)', self.nic_log).group(1)
        self.businfo = PciePaser(self.bus, True).as_dict()
        self.portinfo = NICPort(self.portname).as_dict()
        self.nicinfo.update(self.businfo)
        self.nicinfo.update({'PortInfo': self.portinfo})

    def as_dict(self):
        return self.nicinfo


class NICPort(object):
    def __init__(self, portname):
        self.portname = portname
        self.nic_log = os.popen('ethtool -i ' + portname).read()
        self.bus = re.search('bus-info: (.*)', self.nic_log).group(1)
        self.driver = re.search('driver: (.*)', self.nic_log).group(1)
        self.driver_ver = re.search('version: (.*)', self.nic_log).group(1)
        self.ip = self._get_ip()
        self.netmask = self._get_netmask()
        self.mac = os.popen('cat /sys/class/net/'+portname+'/address').read().strip()
        self.speed = os.popen('cat /sys/class/net/'+portname+'/speed').read().strip()
        self.pn = self._get_pn()
        self.sn = self._get_sn()
        self.model = os.popen('lspci -s ' + self.bus + '| awk \'{print $4,$6}\'').read().strip()
        self.firmware = re.search('firmware-version: (.*)', self.nic_log).group(1)

    def __repr__(self):
        """Define a basic representation of the class object."""
        return '<%s ethernet device on %s mod:%s sn:%s>' % (self.bus,
                                                        self.portname,
                                                        self.model,
                                                        self.sn)

    def _get_ip(self):
        ifcfg_log = os.popen("ifconfig " + self.portname).read()
        try:
            return re.search("inet (\d+.*?)\s", ifcfg_log, re.M|re.S).group(1)
        except Exception:
            return ''

    def _get_netmask(self):
        ifcfg_log = os.popen("ifconfig " + self.portname).read()
        try:
            return re.search("netmask (\d+.*?)\s", ifcfg_log, re.M|re.S).group(1)
        except Exception:
            return ''

    def _get_pn(self):
        pn = os.popen('lspci -s ' + self.bus + ' -vvv | awk /PN/\'{print $NF}\'').read().strip()
        if not pn:
            pn = 'NULL'
        return pn

    def _get_sn(self):
        sn = os.popen('lspci -s ' + self.bus + ' -vvv | awk /SN/\'{print $NF}\'').read().strip()
        if not sn:
            sn = 'NULL'
        return sn

    def as_dict(self):
        return {'Bus': self.bus,
                'Port': self.portname,
                'IP': self.ip,
                'Net_mask': self.netmask,
                'MAC': self.mac,
                'Speed': self.speed,
                'Firmware': self.firmware,
                'Driver': self.driver,
                'Driver_Version': self.driver_ver
                }


class PciePaser():
    _lspci_mr_command = 'lspci -vmm -s %s'
    _lspci_verbose_command = 'lspci -v -s %s'
    _lspci_vverbose_command = 'lspci -vv -s %s'

    def __init__(self, slot, search_spd=False):
        self.slot = slot
        self.search_spd = search_spd
        self.__info = {}
        self.LnkSta = {}
        self.LnkCap = {}
        self.SN = 'NULL'
        self.PN = 'NULL'
        self.Aer = {}
        self.parser(slot)

    def parser(self, slot):
        for line in exec_command(self._lspci_mr_command % slot).split('\n'):
            parts = line.partition(':')
            if parts[0]:
                self.__info[parts[0].strip()] = parts[2].strip()

        verbose = exec_command(self._lspci_vverbose_command % slot)
        lnkcap_speed = re.search('LnkCap.*Speed (\d.*?GT/s)', verbose).group(1)
        lnkcap_width = re.search('LnkCap.*Width (x\d+)', verbose).group(1)
        self.__info['LnkCap_Speed'] = lnkcap_speed
        self.__info['LnkCap_Width'] = lnkcap_width
        lnksta_speed = re.search('LnkSta.*Speed (\d.*?GT/s)', verbose).group(1)
        lnksta_width = re.search('LnkSta.*Width (x\d+)', verbose).group(1)
        self.__info['LnkSta_Speed'] = lnksta_speed
        self.__info['LnkSta_Width'] = lnksta_width
        UeSta = re.search('UESta:(.*)', verbose).group(1)
        UeMsk = re.search('UEMsk:(.*)', verbose).group(1)
        CeSta = re.search('CESta:(.*)', verbose).group(1)
        CeMsk = re.search('CEMsk:(.*)', verbose).group(1)
        self.Aer['UeSta'] = UeSta
        self.Aer['UeMsk'] = UeMsk
        self.Aer['CeSta'] = CeSta
        self.Aer['CeMsk'] = CeMsk
        if self.search_spd:
            PN = re.search('Part number:(.*?)', verbose)
            if PN:
                self.PN = PN.group(1)
            SN = re.search('Serial bumber:(.*?)', verbose)
            if SN:
                self.SN = SN.group(1)

    def as_dict(self):
        if self.search_spd:
            self.__info.update({'PN': self.PN, 'SN': self.SN})
            return self.__info

        else:
            return self.__info


class NICInfo(StdInfo):
    def __init__(self):
        self.name = 'Ethernet Information'
        self.log = logging.getLogger('hwinfo.nic')
        self.Maximum = 0
        self._nics = []
        self.all_interface = []
        self.businfo = []
        self.portinfo = []
        self.nicinfo = []

    def get_interface(self):
        for interface in glob.glob("/sys/class/net/[ei]*"):
            self.all_interface.append(interface.split(os.sep)[-1])
        return self.all_interface

    def parse(self):
        self.get_interface()
        for interface in self.all_interface:
            self._nics.append(NIC(interface))

    def get_details(self):
        for nic in self._nics:
            self.nicinfo.append(nic.as_dict())
        return self.nicinfo

    def get_businfo(self):
        for nic in self._nics:
            self.businfo.append(nic.businfo)
        return self.businfo

    def get_portinfo(self):
        for nic in self._nics:
            self.portinfo.append(nic.portinfo)
        return self.portinfo

    def __repr__(self):
        """Define a basic representation of the class object."""
        rep = '<NICList contents:\n'
        for device in self._nics:
            rep += str(device) + '\n'
        return rep + '>'

    def show_details(self):
        if self.nicinfo:
            table = PrettyTable()
            table.title = self.name
            table.field_names = list(self.nicinfo[0].keys())
            for nic in self.nicinfo:
                table.add_row(nic.values())
            self.log.info('\n'+ str(table))


if __name__ == '__main__':
    import json
    from utils import log_to_file
    log_to_file('log/nic_info.log')
    nic = NICInfo()
    nic.parse()
    print(json.dumps(nic.get_details(),indent=4))
    nic.show_details()
