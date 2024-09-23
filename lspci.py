import logging
import re
import json
import subprocess
import os
import sys
import collections
from utils import *
logger = logging.getLogger(__name__)


class ListPCI():
    def __init__(self):
        self.pci_devices = collections.defaultdict()
        self.get_initial_list()

    def get_initial_list(self):
        """
        @brief      Get a condensed list of devices

        @param      self  The object

        @return     The initial list.
        """
        logger.info('Scanning PCI bus for device info')
        lspci_out = exec_command('sudo /sbin/lspci')
        for line in lspci_out.split('\n'):
            words_in_line = line.split()
            if words_in_line:
                bdf = words_in_line[0]
                self.get_device_details(bdf)

    def get_device_details(self, bdf):
        """
        @brief      pull detailed device info for target device at bdf

        @param      bdf     bus:device.function of pci device
        """
        dev_header = collections.defaultdict()
        command = 'sudo /sbin/lspci -s %s -xxxxvvvvnn' % bdf
        lspci_v_out = exec_command(command)
        self.parse_lspci_details(bdf, lspci_v_out, dev_header)

    def parse_lspci_details(self, bdf, lspci_v_out, dev_header):
        """
        @brief      parse detailed device info for target device at bdf

        @param      bdf            bus:device.function of pci device
        @param      lspci_v_out    verbose lspci output
        @param      dev_header     parsed device container
        """
        current_capability_info = collections.defaultdict()
        device_info = []
        line_count = 1
        config_space_data = []
        has_capabilities = 0
        for line in lspci_v_out.split('\n'):
            if line.strip():
                leading_spaces = len(line) - len(line.lstrip())
                if line_count == 1:
                    if self.line_by_index(line, ']:'):
                        index, pre, post = self.line_by_index(line, ']:')
                        class_words = pre.split()
                        class_text = class_words[1:]
                        new_class_text = ' '.join(map(str, class_text))
                        new_class_text = new_class_text.replace(':', '')
                        dev_header.update({'Class String': new_class_text})
                        device_words = post
                        dev_header.update({'Device String': device_words})
                        if self.line_by_index(post, ':'):
                            index, prev, postv = self.line_by_index(post, ':')
                            if ':' in index:
                                vendor_device = index.split(':')
                                vendor_id = vendor_device[0].replace('[', '')
                                device_id = vendor_device[1].replace(']', '')
                                dev_header.update({'Vendor ID': vendor_id})
                                dev_header.update({'Device ID': device_id})
                if line_count == 2:
                    if self.line_by_index(line, 'Subsystem:'):
                        index, pre, post = self.line_by_index(line, 'Subsystem:')
                        sub_words = post.split()
                        sub_text = sub_words[0:]
                        new_sub_text = ' '.join(map(str, sub_text))
                        dev_header.update({'Subsystem': new_sub_text})
                        if self.line_by_index(new_sub_text, ':'):
                            index, prev, post = self.line_by_index(new_sub_text, ':')
                            if ':' in index:
                                sub_vendor_device = index.split(':')
                                sub_vendor_id = sub_vendor_device[0].replace('[', '')
                                dev_header.update({'Subsystem Vendor': sub_vendor_id})
                                sub_device_id = sub_vendor_device[1].replace(']', '')
                                dev_header.update({'Subsystem Device': sub_device_id})
                elif line_count != 1 and line_count != 2 and leading_spaces == 1:
                    if self.line_by_index(line, ':'):
                        index, pre, post = self.line_by_index(line, ':')
                        key = pre.replace(':', '')
                        value = post
                        if key == 'Capabilities':
                            if has_capabilities != 0:
                                device_info.append(current_capability_info.copy())
                                current_capability_info.clear()
                            current_capability_info.update({key: value})
                            has_capabilities += 1
                        elif 'Kernel driver in use' in key:
                            if current_capability_info:
                                device_info.append(current_capability_info.copy())
                                current_capability_info.clear()
                            dev_header.update({key: value})
                        else:
                            dev_header.update({key: value})
                elif line_count != 1 and line_count != 2 and leading_spaces == 0:
                    if config_space_data:
                        config_space_data.append(line)
                    else:
                        if current_capability_info:
                            device_info.append(current_capability_info.copy())
                            current_capability_info.clear()
                        config_space_data.append(line)
                elif leading_spaces >= 2:
                    if self.line_by_index(line, ':'):
                        index, pre, post = self.line_by_index(line, ':')
                        key = pre.replace(':', '')
                        value = post
                        current_capability_info.update({key: value})
                line_count += 1

        dev_header.update({'Capabilities': device_info})
        dev_header.update({'PCI Config Space': config_space_data})
        self.pci_devices.update({bdf: dev_header})
        try:
            os.mkdir('pci_logs')
        except:
            pass

        if not os.path.isfile('pci_logs/' + bdf + '.raw'):
            write_to_file('pci_logs/' + bdf + '.raw', lspci_v_out)
        if not os.path.isfile('pci_logs/' + bdf + '.json'):
            with open('pci_logs/' + bdf + '.json', 'w') as f:
                json.dump(dev_header, f, indent=4)
        else:
            return json.dumps(dev_header, indent=4)

    def line_by_index(self, line, index_val):
        words = line.split()
        for word in words:
            if index_val in str(word):
                index = words.index(word)
                pre_index_text = words[0:index + 1]
                new_pre_index_text = ' '.join(map(str, pre_index_text))
                post_index_text = words[index + 1:]
                new_post_index_text = ' '.join(map(str, post_index_text))
                index = words[index]
                return (index, new_pre_index_text, new_post_index_text)

        return False

    def merge_dicts(self, *dict_args):
        """
        @brief      Given any number of dicts, shallow copy and merge into a new
                    dict

        @param      self       The object
        @param      dict_args  The dictionary arguments

        @return     { description_of_the_return_value }
        """
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)

        return result

    def return_target_attribute_value(self, bdf, key):
        """
        @brief      returns the saved attribute details regarding device at bdf

        @param      self  The object
        @param      bdf   The bdf
        @param      key   The key

        @return     { description_of_the_return_value }
        """
        output = self.search_for_target_bdf(bdf)
        return output.get(key)

    def search_for_all_matching_device(self, search):
        matches = collections.defaultdict()
        for bdf in self.pci_devices:
            for device in self.pci_devices.values():
                if search in device.keys():
                    matches.update({bdf: search + ' found in key'})
                if search in device.values():
                    matches.update({bdf: search + ' found in value'})
                else:
                    output = self.return_target_attribute_value(bdf, 'Capabilities')
                    for dict in output:
                        if search in dict:
                            matches.update({bdf: search + ' found in capabilities'})

        return matches

    def search_for_target_vendor(self, vsearch):
        matches = []
        for bdf in self.pci_devices:
            vendor_id = self.return_target_attribute_value(bdf, 'Vendor ID')
            if vsearch == vendor_id:
                fn = bdf.split('.')[-1]
                if fn == '0':
                    matches.append(bdf)

        return matches

    def search_for_target_vendor_device(self, vsearch, dsearch):
        matches = []
        for bdf in self.pci_devices:
            vendor_id = self.return_target_attribute_value(bdf, 'Vendor ID')
            device_id = self.return_target_attribute_value(bdf, 'Device ID')
            if vsearch == vendor_id and dsearch == device_id:
                matches.append(bdf)

        return matches

    def search_for_target_bdf(self, bdf):
        """
        retrieve the saved details regarding device at bdf

        @param      self  The object
        @param      bdf   The bdf

        @return     { description_of_the_return_value }
        """
        if bdf in self.pci_devices:
            return self.pci_devices[bdf]

    def search_target_capability(self, bdf, cap, key):
        """
        returns the target value for a target capability attribute key

        @param      self  The object
        @param      bdf   The bdf
        @param      cap   The capability
        @param      key   The key

        @return     { description_of_the_return_value }
        """
        output = self.return_target_attribute_value(bdf, 'Capabilities')
        for dict in output:
            print(dict)
            if cap in dict['Capabilities']:
                if key in dict:
                    return dict[key]

    def check_width(self, bdf, cap, search):
        """
        @brief      returns width capability

        @usage

        @param      bdf         bus:device.function targeted
        @param      cap         target capability
        @param      search      search term
        """
        output = self.search_target_capability(bdf, cap, search)
        words = output.split(',')
        for word in words:
            if 'Width' in word:
                index, pre, post = self.line_by_index(word, '')
                return post

    def check_width_match(self, bdf, cap, c_search, s_search):
        """
        @brief      boolean check on width capability vs status

        @param      self      The object
        @param      bdf       The bdf
        @param      cap       The capability
        @param      c_search  The c search
        @param      s_search  The s search

        @return     boolean
        """
        cap_width = self.check_width(bdf, cap, c_search)
        status_width = self.check_width(bdf, cap, s_search)
        if cap_width == status_width:
            return True
        else:
            logger.debug('Status %s does not match capability %s' % (cap_width, status_width))
            return False


class LSPCI():
    """
    Abstracts lspci controller information.
    """
    _capability_types_re = '(.*)((Power Management)|(Endpoint, MSI)|(Advanced Error Reporting))(.*)'
    _capability_params_re = '(.*)((Lnk)|(Flags)|(Status)|([UC]E))(.*)'
    _controller_desc_pattern = '(.*?)(scsi|sas|sata|eth|non\\-volatile)(.*)'
    _lspci_command = 'lspci'
    _lspci_mr_command = 'lspci -vmm -s %s'
    _lspci_verbose_command = 'lspci -v -s %s'
    _lspci_vverbose_command = 'lspci -vv -s %s'
    _controller_search_str = 'control'
    _lspci_key_str = 'lspci'
    _lspci_ctrlr_key_str = 'controllers'
    _capab_search_str = 'Capabilities:'

    def __init__(self):
        self.__controllers = []
        self.init_controllers()

    def init_controllers(self):
        """
        Initializes controller info.
        """
        raw_log = exec_command(LSPCI._lspci_command)
        for line in raw_log.split('\n'):
            if LSPCI._controller_search_str in line.lower():
                if re.match(LSPCI._controller_desc_pattern, line.lower()):
                    info = line.partition(' ')
                    logger.debug('Controller found, slot: %s' % info[0])
                    ctrlr = LSPCIController(info[0])
                    if ctrlr.has_capabilities:
                        self.__controllers.append(ctrlr)

    def as_dict(self, flatten = False):
        """
        For serialization.
        """
        c_list = []
        if flatten:
            flat_dict = {}
            for ctrlr in self.__controllers:
                ctrlr_dict = ctrlr.as_dict(flatten=True)
                for key in ctrlr_dict.keys():
                    flat_dict['%s.%s' % (LSPCI._lspci_ctrlr_key_str, key)] = ctrlr_dict[key].replace(',', ';')

            return flat_dict
        for ctrlr in self.__controllers:
            c_list.append(ctrlr.as_dict())

        return {LSPCI._lspci_ctrlr_key_str: {LSPCI._lspci_ctrlr_key_str: c_list}}

    @classmethod
    def parse_raw_log(cls):
        try:
            return LSPCI()
        except Exception as e:
            logger.exception(e)
            return None

        return None


class LSPCIController():
    """
    Abstracts the information of each lspci controller.
    """
    _flat_keys_info = ['Device']
    _flat_keys_attr = ['Kernel driver in use']
    _flat_regex_caps = '(.*)(Endpoint, MSI)(.*)'
    _flat_regex_caps_attr = '(.*)(LnkCap|LnkSta)(.*)'

    def __init__(self, slot):
        self.__info = {}
        self.__slot = slot
        self.__attributes = []
        self.__attr_dict = {}
        self.__capabilities = []
        self.init_controller_info(slot)

    def init_controller_info(self, slot):
        """
        Gets the detailed information for each controller.
        """
        for line in exec_command(LSPCI._lspci_mr_command % slot).split('\n'):
            parts = line.partition(':')
            if parts[0]:
                self.__info[parts[0].strip()] = parts[2].strip()

        for line in exec_command(LSPCI._lspci_verbose_command % self.__slot).split('\n')[1:]:
            line = line.strip()
            if line and LSPCI._capab_search_str not in line:
                if ':' in line:
                    parts = line.partition(':')
                    self.__attr_dict[parts[0].strip()] = parts[2].strip()
                self.__attributes.append(line)

        verbose = exec_command(LSPCI._lspci_vverbose_command % self.__slot)
        caps_desc = verbose.split(LSPCI._capab_search_str)
        for cap in caps_desc:
            cap = cap.strip()
            if cap.startswith('[') and re.match(LSPCI._capability_types_re, cap):
                self.__capabilities.append(LSPCISlotCapability(cap))

    def has_capabilities(self):
        return len(self.__capabilities) > 0

    def as_dict(self, flatten=False):
        if flatten:
            flat_dict = {}
            for key in LSPCIController._flat_keys_info:
                flat_dict['%s.%s' % (self.__slot, key)] = self.__info[key]

            for key in LSPCIController._flat_keys_attr:
                if key in self.__attr_dict:
                    flat_dict['%s.%s' % (self.__slot, key)] = self.__attr_dict[key]

            for cap in self.__capabilities:
                cap_dict = cap.as_dict()
                for key in cap_dict.keys():
                    if re.match(LSPCIController._flat_regex_caps, key):
                        cap_attr_dict = cap_dict[key]
                        for attr in cap_attr_dict.keys():
                            if re.match(LSPCIController._flat_regex_caps_attr, attr):
                                flat_dict['%s.Capabilities[%s].%s' % (self.__slot, key.replace(',', ':'), attr)] = \
                                cap_attr_dict[attr].replace(',', ';')

            return flat_dict
        return {self.__slot: {'slot_info': self.__info,
                              'attributes': [attr for attr in self.__attributes],
                              'capabilities': create_dict_from_list(self.__capabilities)}}


class LSPCISlotCapability():
    """
    Abstracts an indiviual capability for a device.
    """

    def __init__(self, raw_log):
        """
        Example raw_log:
        [e0] Express (v1) Endpoint, MSI 00
                DevSta: CorrErr+ UncorrErr- FatalErr- UnsuppReq+ AuxPwr+ TransPend-
                LnkCap: Port #1, Speed 2.5GT/s, Width x1, ASPM L0s L1, Latency L0 <128ns, L1 <64us
                        ClockPM- Surprise- LLActRep- BwNot-

        """
        raw_log_parts = raw_log.partition('\n')
        self.__cap_desc = raw_log_parts[0]
        raw_log_desc = raw_log_parts[2].replace('\n\t\t\t', ' ')
        self.__params = []
        for line in raw_log_desc.split('\n'):
            param_tuple = line.partition(':')
            if re.match(LSPCI._capability_params_re, param_tuple[0]):
                self.__params.append(Parameter('', param_tuple[0].strip(), param_tuple[2].strip()))

    def as_dict(self, flatten=False):
        return {self.__cap_desc: create_dict_from_list(self.__params, flatten)}


if __name__ == '__main__':
    # ListPCI().check_width_match('3d:00.0', '[a0] Express (v2) Endpoint,', 'LnkCap', 'LnkSta')
    print(json.dumps(LSPCI().as_dict(), indent=0))