import os
import re
import sys
import glob
import logging
from prettytable import PrettyTable
from collections import OrderedDict
from std_info import StdInfo
from utils import exec_command, dmidecode_parser

log = logging.getLogger('hwinfo.hba')
LIST_TIMEOUT = 10
DUMP_TIMEOUT = 30


def get_path(relative_path):
    try:
        base_path = sys._MEIPASS # pyinstaller打包后的路径
    except AttributeError:
        base_path = os.path.abspath(".") # 当前工作目录的路径
 
    return os.path.normpath(os.path.join(base_path, relative_path)) # 返回实际路径



class HbaInfo(StdInfo):
    tool = '/usr/bin/lsiutil'
    fw_sum_size = 790528
    search_str = [85, 170]
    div_offset = 51200
    rom_file = 'rom_dump.bin'
    fw_sha256 = None
    bios_sha256 = None
    device_list = []
    bus_info = []
    def __init__(self):
        self.name = 'HBA Information'
        self._hbas = []
        self.log = logging.getLogger('hwinfo.hba')
        self.hbainfo = []

    @classmethod
    def supported(cls):
        result = os.path.isfile(cls.tool)
        return result

    def parse(self):
        self.log.info('#hba(raid) information')
        lsi = LSIFirmware()
        self.hbainfo = lsi.details()

    def get_details(self):
        return self.hbainfo

    def show_details(self):
        if self.hbainfo:
            table = PrettyTable()
            table.title = self.name
            table.field_names = list(self.hbainfo[0].keys())
            for hba in self.hbainfo:
                table.add_row(hba.values())
            self.log.info('\n'+ str(table))


class HbaInfo_old(object):
    tool = 'tool/lsiutil'
    fw_sum_size = 790528
    search_str = [85, 170]
    div_offset = 51200
    rom_file = 'rom_dump.bin'
    fw_sha256 = None
    bios_sha256 = None
    device_list = []
    bus_info = []

    def __init__(self):
        filename = __file__.split('/')[-1]
        cut = '.py'
        if '.pyc' in filename:
            cut = '.pyc'
        filename = filename.strip(cut)
        self.log = logging.getLogger(__name__)
        self.log.debug('DEBUG FwHbaService')
        self.device_list = self._get_hba_info()
        self.info_details = self.get_details()

    @classmethod
    def supported(cls):
        result = os.path.isfile(cls.tool)
        return result

    def _get_hba_info(self):
        lsi = LSIFirmware()
        return lsi.details()

    def get_details(self):
        hba_sha = {}
        for i in range(0, len(self.device_list)):
            device = i + 1
            hba = self.device_list[i]
            fw = {'firmware': []}
            fw_rev = {'version': hba['Firmware Rev'],
             'type': 'Firmware Rev'}
            fw['firmware'].append(fw_rev)
            mpt_rev = {'version': hba['MPT Rev'],
             'type': 'MPT Rev'}
            fw['firmware'].append(mpt_rev)
            hba.pop('Firmware')
            hba.pop('Firmware Rev')
            hba.pop('BIOS')
            hba.pop('BIOS Date')
            hba.pop('MPT Rev')
            hba['bus'] = hba.pop('PCI id')
            hba['model'] = hba.pop('Type')
            hba.update(fw)
            self.device_list[i] = hba
        return self.device_list

    def show(self, file=sys.stdout):
        pass


class LSIFirmware(object):
    timeout = 120

    def probe(self):
        return self.has_lsi()

    def has_lsi(self):
        lspci_raw = os.popen('lspci').split('\n')
        lsi_pci = re.compile('.*LSI.*SAS.*')
        for line in lspci_raw:
            if lsi_pci.search(line):
                return True
        return False

    def details(self):
        card_count = 0
        hba_types = list()
        hba_firmwares = list()
        hba_bios = list()
        hba_bios_dates = list()
        hba_pci_ids = list()
        hba_firmware_revs = list()
        hba_mpt_revs = list()
        adapters = list()
        lspci_loc = os.popen('which lsiutil 2>/dev/null')
        if lspci_loc.read():
            arg = lspci_loc.read().strip()
        else:
            arg = get_path('tool/lsiutil')
        cmd_arg = '%s 1 59' % arg
        cmdout = os.popen(cmd_arg)
        # self.lsiutil = cmdout.read()
        for line in cmdout.read().split('\n'):
            a = re.search('(\\d+)[a-zA-Z ]+Ports? found', line)
            b = re.search('^ \\d+.', line)
            c = re.search('Current active firmware version is.*\\(([\\d+\\.]+\\d+)\\)', line)
            d = re.search('.*BIOS.*version.*-([\\d+\\.]+\\d+) \\((\\d{4}\\.\\d{2}\\.\\d{2})\\)', line)
            e = re.search('^PCI location is Segment\\ (\\d+), Bus\\ (\\d+), Device (\\d+), Function (\\d+) \\(combined:\\s([0-9a-fA-F]+)\\)', line)
            if a:
                card_count = int(a.group(1))
                log.debug('FOUND %d CARDS' % card_count)
            if b:
                hba_types.append(re.split('\\s{2,}', line)[2])
                hba_firmware_revs.append(re.split('\\s{2,}', line)[3])
                hba_mpt_revs.append(re.split('\\s{2,}', line)[4])
            if c:
                hba_firmwares.append(c.group(1))
            if d:
                hba_bios.append(d.group(1))
                hba_bios_dates.append(d.group(2))
            if e:
                s1 = '{0:04x}:{1:02x}:{2:02x}:{3:01x}'.format(int(e.group(1)), int(e.group(2)), int(e.group(3)), int(e.group(4)))
                hba_pci_ids.append(s1)

        for i in range(card_count):
            try:
                hba_type = hba_types[i]
            except IndexError as e:
                hba_type = ''
                log.error('No index %s' % e)

            try:
                hba_firmware = hba_firmwares[i]
            except IndexError as e:
                hba_firmware = ''
                log.error('No hba firmware for card %s' % i)

            try:
                hba_b = hba_bios[i]
            except IndexError as e:
                hba_b = ''
                log.error('No index %s' % e)

            try:
                hba_bios_date = hba_bios_dates[i]
            except IndexError as e:
                hba_bios_date = ''
                log.error('No index %s' % e)

            try:
                hba_pci_id = hba_pci_ids[i]
            except IndexError as e:
                hba_pci_id = ''
                log.error('No index %s' % e)

            try:
                hba_firmware_rev = hba_firmware_revs[i]
            except IndexError as e:
                hba_firmware_rev = ''
                log.error('No index %s' % e)

            try:
                hba_mpt_rev = hba_mpt_revs[i]
            except IndexError as e:
                hba_mpt_rev = ''
                log.error('No index %s' % e)

            adapters.append({'Type': hba_type,
             'Firmware': hba_firmware,
             'BIOS': hba_b,
             'BIOS Date': hba_bios_date,
             'PCI id': hba_pci_id,
             'Firmware Rev': hba_firmware_rev,
             'MPT Rev': hba_mpt_rev})
        # print(adapters)
        return adapters


if __name__ == '__main__':
    import json
    from utils import log_to_file
    log_to_file('log/hba_info.log')
    hba = HbaInfo()
    # if hba.supported():
    hba.parse()
    print(hba.get_details())
    hba.show_details()