from collections import OrderedDict
import json
import re
import os
import subprocess
from subprocess import Popen, PIPE
import platform
from utils import exec_command
smartctl_type = {'ata': 'ata',
                 'csmi': 'ata',
                 'sas': 'scsi',
                 'sat': 'sat',
                 'sata': 'ata',
                 'scsi': 'scsi',
                 'atacam': 'atacam'}


class Attribute(object):
    """
    Contains all of the information associated with a signgile SMART attribute
    in a `Device`'s SMART table. This data is intended to exactly mirror that abtained through smartctl.
    """
    def __init__(self, num, name, flags, value, worst, thresh, attr_type, updated, when_failed, raw):
        self.num = num
        self.name = name
        self.flags = flags
        self.value = value
        self.worst = worst
        self.thresh = thresh
        self.type = attr_type
        self.updated = updated
        self.when_failed = when_failed
        self.raw = raw

    def __repr__(self):
        """ Define a basic representation of the class object."""
        return '<SMART Attribute %r %s/%s raw:%s>'% (self.name,
                                                          self.value,
                                                          self.thresh,
                                                          self.raw)

    def __str__(self):
        """Define a formatted string representation of the object's content.
        In the interest of not overflowing 80-character lines this does not
        print the value of `pySMART.attribute.flags_hex"""
        return "{0:>3} {1:24}{2:4}{3:4}{4:4}{5:9}{6:8}{7:12}{8}".format(self.num, self.name, self.value, self.worst,
                                                                        self.thresh, self.type, self.updated,
                                                                        self.when_failed, self.raw)

    def as_dict(self):
        return {'ID': self.num,
                'Name': self.name,
                'Value': self.value,
                'Worst': self.worst,
                'Thresh': self.thresh,
                'Type': self.type,
                'Updated': self.updated,
                'When_failed': self.when_failed,
                'Raw': self.raw}


class NVMe(object):
    """
    Represents any device attached to an internal storage interface, such as a
    hard drive or DVD-ROM, and detected by smartmontools. Includes eSATA
    (considered SATA) but excludes other external devices (USB, Firewire).
    """

    def __init__(self, name):
        """Instantiates and initializes the `pySMART.device.Device`."""
        self.name = name.replace('/dev/', '')
        self.manu = None
        self.model = None
        self.serial = None
        self.controler = None
        self.capacity = None
        self.firmware = None
        self.inteface = None
        self.numa_node = None
        self.cpulists = None
        self.root_bus = None
        self.dev_bdf = None
        self.lnkcap = None
        self.lnksta = None
        self.aer = {}
        self.attributes = {}
        self.update()

    def update(self):
        base_path = '/sys/class/nvme'
        self.bus_output = subprocess.getstatusoutput('ls -l /sys/block | grep ' + self.name)[1].split('/')
        self.root_bus = self.bus_output[3]
        self.dev_bdf = self.bus_output[-4]
        self.controler = self.bus_output[-2]
        ctl_path = os.path.join(base_path, self.controler)
        self.model = self._get_val(ctl_path, 'model')
        self.manu = self.model.split()[0]
        self.serial = self._get_val(ctl_path, 'serial')
        self.firmware = self._get_val(ctl_path, 'firmware_rev')
        self.inteface = self._get_val(ctl_path, 'transport')
        smctl_info = subprocess.getstatusoutput("smartctl -a /dev/{0}".format(self.name))
        self.capacity = re.search("Total.*?\[(.*?)\]", smctl_info[1]).group(1)
        # print(self.capacity)
        dev_path = os.path.join(ctl_path, 'device')
        self.current_link_speed = self._get_val(dev_path, 'current_link_speed')
        self.current_link_width = self._get_val(dev_path, 'current_link_width')
        self.max_link_speed = self._get_val(dev_path, 'max_link_speed')
        self.max_link_width = self._get_val(dev_path, 'max_link_width')
        self.numa_node = self._get_val(dev_path, 'numa_node')
        self.cpulists = self._get_val(dev_path, 'local_cpulist')
        smart_log = subprocess.getstatusoutput("nvme smart-log /dev/%s | sed 1d" % self.name)[1]
        self.attributes = {}
        for line in smart_log.split('\n'):
            tmp = line.split(':')
            if len(tmp) == 2:
                self.attributes[tmp[0].strip(' ')] = re.match('\d+', tmp[1].strip(' ')).group(0)

    def bus_info(self):
        self.bus_details = {}
        self.values = {}
        self.values.update({'bdf': self.dev_bdf})
        lspci_info = subprocess.getstatusoutput("lspci -s {0} -vv".format(self.dev_bdf))[1]
        for line in lspci_info.split('\n'):
            if 'LnkCap:' in line:
                self.lnkcap = line.split(',')[1:3]
                self.lnkcap = [x.strip() for x in self.lnkcap]
                self.values.update({'LinkCap': self.lnkcap})
            if 'LnkSta:' in line:
                self.lnksta = line.split(',')[1:3]
                self.lnksta = [re.sub('\\(.*?\\)', '', x.strip()) for x in self.lnksta]
                self.values.update({'LnkSta': self.lnksta})
            if 'UESta:' in line:
                val = line.split(':')[1].strip().split()
                self.aer.update({'UESta': val})
            if 'CESta:' in line:
                val = line.split(':')[1].strip().split()
                self.aer.update({'CESta': val})
        self.values.update({'aer': self.aer})
        return self.values

    @property
    def smartvalues(self):
        return {self.name: self.attributes}

    @property
    def criticalsmartvalues(self):
        smart_values = ['critical_warning', 'temperature', 'available_spare', 'media_error', 'num_err_log_entries']
        criticalvalues = {}
        for name, val in self.attributes.items():
            if name in smart_values:
                criticalvalues.update({name: val})
        return criticalvalues

    def as_dict(self, withsmart=False):
        ret = OrderedDict()
        ret.update({'dev': '/dev/' + self.name,
                'manufacturer': self.manu,
                'model': self.model,
                'serialnumber': self.serial,
                'capacity': self.capacity,
                'firmware': self.firmware,
                'numa_node': self.numa_node,
                'bdf': self.dev_bdf})
                # 'max_speed': self.max_link_speed,
                # 'max_width': self.max_link_width,
                # 'sta_speed': self.current_link_speed,
                # 'sta_width': self.current_link_width})
        if withsmart:
            ret.update({'smart': self.attributes})
        return ret

    @staticmethod
    def _get_val(path, name):
        return os.popen('cat ' + os.path.join(path, name)).read().strip()


class HDDInfoTemplate(object):
    def __init__(self):
        self.Logical = None
        self.Manufacturer = None
        self.Model = None
        self.Firmware = None
        self.Capacity = None
        self.Link = None
        self.RPM = None
        self.SerialNumber = None

    def parse(self):
        ret = OrderedDict()
        ret["Logical"] = self.Logical
        ret["Manufacturer"] = self.Manufacturer
        ret["Model"] = self.Model
        ret["SerialNumber"] = self.SerialNumber
        ret["Size"] = self.Capacity
        ret['Firmware'] = self.Firmware
        ret["RPM"] = self.RPM
        ret['LinkSpeed'] = self.Link
        return ret


class Device(object):
    def __init__(self, name, interface=None):
        if not (interface is None or interface.lower() in ('ata', 'csmi', 'sas', 'sat', 'sata', 'scsi')):
            raise AssertionError
        self.name = name.replace('/dev/', '')
        self.manu = None
        self.model = None
        self.serial = None
        self.interface = interface
        self.capacity = None
        self.firmware = None
        self.linkspeed = None
        self.assessment = None
        self.smart_capable = False
        self.smart_enabled = False
        self.is_ssd = None
        self.rotation_rate = None
        self.attributes = [None] * 256
        if self.interface is None:
            _grep = 'find' if platform.system() == 'Windows' else 'grep'
            cmd = subprocess.Popen('smartctl --scan-open | {0} "{1}"'.format(_grep, self.name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _stdout, _stderr = [ i.decode('utf8') for i in cmd.communicate() ]
            if _stdout != '':
                self.interface = _stdout.split(' ')[2]
                self._classify()
            else:
                return
        if self.interface is not None:
            self.update()
        return

    def _classify(self):
        """
        Disambiguates generic device types ATA and SCSI into more specific ATA, SATA, SAS, SAT and SCSI.
        :return:
        """
        if self.interface in ('scsi', 'ata'):
            test = 'sat' if self.interface == 'scsi' else 'sata'
            cmd = subprocess.Popen('smartctl -d {0} -l sataphy /dev/{1}'.format(smartctl_type[self.interface], self.name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _stdout, _stderr = [ i.decode('utf8') for i in cmd.communicate() ]
            if 'GP Log 0x11' in _stdout.split('\n')[3]:
                self.interface = test
        if self.interface == 'scsi':
            cmd = subprocess.Popen('smartctl -d scsi -l sataphy /dev/{0}'.format(self.name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _stdout, _stderr = [ i.decode('utf8') for i in cmd.communicate() ]
            if 'SAS SSP' in _stdout.split('\n')[4]:
                self.interface = 'sas'
            else:
                cmd = subprocess.Popen('smartctl -d scsi -a /dev/{0}'.format(self.name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _stdout, _stderr = [ i.decode('utf8') for i in cmd.communicate() ]
                for line in _stdout.split('\n'):
                    if 'Transport protocol' in line and 'SAS' in line:
                        self.interface = 'sas'

    def __repr__(self):
        """Define a basic representation of the class object."""
        return '<%s device on /dev/%s mod:%s sn:%s>' % (self.interface.upper(),
                                                        self.name,
                                                        self.model,
                                                        self.serial)

    def as_dict(self):
        ret = OrderedDict()
        ret["Logical"] = self.name
        ret["Manufacturer"] = self.manu
        ret["Model"] = self.model
        ret["SerialNumber"] = self.serial
        ret["Size"] = self.capacity
        ret['Firmware'] = self.firmware
        ret["RPM"] = self.rotation_rate
        ret['LinkSpeed'] = self.linkspeed
        return ret

    def get_attribute_all(self):
        header_printed = False
        allattribute = []
        for attr in self.attributes:
            if attr is not None:
                if not header_printed:
                    allattribute.append(attr.as_dict())
        return allattribute

    def get_attribute_from_id(self, id):
        pass

    def get_attribute_from_name(self, name):
        pass

    def smart_toggle(self, action):
        """
        A basic function to enable/disable SMART on device.

        ##Args:
        * **action (str):** Can be either 'on'(for enabling) or 'off'(for disabling).

        ##Returns"
        * **(bool):** Return True (if action succeded) else False
        * **(str):** None if option succeded else contains the error message.
        """
        action_lower = action.lower()
        if action_lower not in ('on', 'off'):
            return (False, 'Unsupported action {0}'.format(action))
        if self.smart_enabled:
            if action_lower == 'on':
                return (True, None)
        elif action_lower == 'off':
            return (True, None)
        cmd = Popen('smartctl -d {0} -s {1} {2}'.format(smartctl_type[self.interface], action_lower, self.name),
                    shell=True, stdout=PIPE, stderr=PIPE)
        _stdout, _stderr = [i.decode('utf8') for i in cmd.communicate()]
        if cmd.returncode != 0:
            return (False, _stdout + _stderr)
        self.update()
        if action_lower == 'off' and self.smart_enabled:
            return (False, 'Failed to turn SMART off.')
        elif action_lower == 'on' and not self.smart_enabled:
            return (False, 'Failed to turn SMART on.')
        else:
            return (True, None)

    def print_all_attributes(self):
        """
        Prints the entire SMART attribute table, in a format similar to
        the output of smartctl.
        """
        header_printed = False
        for attr in self.attributes:
            if attr is not None:
                if not header_printed:
                    print(
                        '{0:>3} {1:24}{2:4}{3:4}{4:4}{5:9}{6:8}{7:12}{8}'.format('ID#', 'ATTRIBUTE_NAME', 'CUR', 'WST',
                                                                                 'THR', 'TYPE', 'UPDATED', 'WHEN_FAIL',
                                                                                 'RAW'))
                    header_printed = True
                print(attr)

        if not header_printed:
            print('This device does not support SMART attributes.')
        return

    def update(self):
        interface = smartctl_type[self.interface]
        cmd = subprocess.Popen('smartctl -d {0} -a /dev/{1}'.format(smartctl_type[interface], self.name),
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _stdout, _stderr = [i.decode('utf8') for i in cmd.communicate()]
        for line in _stdout.split('\n'):
            if 'Model Family' in line:
                self.manu = line.split(':')[1].split()[0]
            if 'Device Model' in line or 'Product' in line:
                self.model = line.split(':')[1].strip()
            if 'Serial Number' in line or 'Serial number' in line:
                self.serial = line.split(':')[1].split()[0].rstrip()
            if 'Firmware Version' in line or 'Revision' in line:
                self.firmware = line.split(':')[1].strip()
            if 'User Capacity' in line:
                self.capacity = line.replace(']', '[').split('[')[1].strip()
            if 'SATA Version is' in line:
                self.linkspeed = line.split(':')[-1].replace(')', '').strip()
            if 'SMART support' in line:
                if 'Unavailable' in line or 'device lacks SMART capability' in line:
                    self.smart_capable = False
                    self.smart_enabled = False
                elif 'Enabled' in line:
                    self.smart_enabled = True
                elif 'Disabled' in line:
                    self.smart_enabled = False
                elif 'Available' in line or 'device has SMART capability' in line:
                    self.smart_capable = True
            if 'does not support SMART' in line:
                self.smart_capable = False
                self.smart_enabled = False
            if 'Rotation Rate' in line:
                if 'Solid State Device' in line:
                    self.is_ssd = True
                elif 'rpm' in line:
                    self.is_ssd = False
                    try:
                        self.rotation_rate = int(line.split(':')[-1].strip()[:-4])
                    except ValueError:
                        self.rotation_rate = None
            if 'SMART overall-health self-assessment' in line:
                if line.split(':')[-1].strip() == 'PASSED':
                    self.assessment = 'PASS'
                else:
                    self.assessment = 'FAIL'
            if 'SMART Health Status' in line:
                if line.split(':')[1].strip() == 'OK':
                    self.assessment = 'PASS'
                else:
                    self.assessment = 'FAIL'
            if '0x0' in line and '_' in line:
                line_ = ' '.join(line.split()).split(' ')
                if '' not in line_:
                    if len(line_) >= 10:
                        self.attributes[int(line_[0])] = Attribute(line_[0], line_[1], line_[2], line_[3], line_[4],
                                                                   line_[5], line_[6], line_[7], line_[8], line_[9])


class CriticalSmartValues(object):
    def __init__(self, drives):
        self.drives = drives
        self.smart_value = ['Current_Pending_Sector', 'UDMA_CRC_Error_Count', 'Reported_Uncorrect']
        self.drive_value = {}

    def get_value(self):
        for drive in self.drives:
            test = Device(drive)
            self.values = {}
            for smart_value in self.smart_value:
                attrib_list = [x for x in test.attributes if x is not None]
                attrib_raw_count = [x.raw for x in attrib_list if smart_value in x.name]
                if attrib_raw_count:
                    self.values.update({smart_value: int(attrib_raw_count[0])})
            self.drive_value.update({drive: self.values})
        return self.drive_value


def discover_disks():
    nvmes = []
    hdds = []
    ssds = []
    sta, res = subprocess.getstatusoutput("lsscsi | awk /disk/'{print $NF}'")
    for disk in res.split('\n'):
        if 'nvme' in disk:
            nvmes.append(disk)
        else:
            devnode = disk.replace("/dev/", '')
            rotational = int(exec_command("cat /sys/block/{}/queue/rotational".format(devnode)))
            if rotational == 1:
                hdds.append(disk)
            else:
                ssds.append(disk)
    return {'NVMe': nvmes, 'HDD': hdds, 'SSD': ssds}


if __name__ == '__main__':
    print(Device('/dev/sda').getinfo())
    print(Device('/dev/sda').get_attribute_all())
    print(CriticalSmartValues(['/dev/sda']).get_value())