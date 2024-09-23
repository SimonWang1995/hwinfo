import os
import logging
from logging import DEBUG
import threading
import subprocess
import re


def exec_command(command, silent=True, ignore=False, asyncflag=False):
    """exec_command(command, silent=True, ignore=False, async=False)

    Description:
        Open a subprocess via Popen, into the OS, to execute a command

    Usage:
        result = exec_command("ls -la")

    Parameters:
        command - Command to pass to the OS as a string
        silent  - Flag to enable (False) or disable (True) logging
                  Default: True
        ignore  - Flag to log (False) or not log (True) errors (stderr)
        async   - Return subprocess Process ID

    Return:
        stdout  - Return the results of the command executed as a list
    """
    # logger.debug("Exec Command: " + command)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if asyncflag:
        return p.pid
    stdout, stderr = [i.decode() for i in p.communicate()]
    if not silent:
        # logger.info('return: \n' + stdout)
        print('return: \n' + stdout)
    if p.returncode != 0 and not ignore:
        # logger.error(stderr)
        raise NameError('%s failed: %s ' % (command, stderr))
    return stdout


def dmidecode_parser(dmimsg):
    dmimsg_list = re.findall("(Handle.*?)\n\n", dmimsg, re.M | re.S)
    # print(dmimsg_list)
    info_list = []
    for dmi_msg in dmimsg_list:
        tmp_dict = {}
        tmp_list = []
        for line in dmi_msg.split('\n')[2:]:
            if ':' in line:
                parts = line.split(':')
                name = parts[0].strip()
                tmp_dict[parts[0].strip()] = parts[1].strip()
                tmp_list = []
            else:
                tmp_list.append(line.strip())
                tmp_dict[name] = tmp_list
        info_list.append(tmp_dict)
    # print(info_list)
    return info_list


_g_thread_data = threading.local()
_g_thread_counter = 0
_g_thread_lock = threading.Lock()


def get_thread_id():
    global _g_thread_data, _g_thread_counter, _g_thread_lock
    try:
        return _g_thread_data.id
    except AttributeError:
        with _g_thread_lock:
            _g_thread_counter += 1
            _g_thread_data.id = _g_thread_counter
        return _g_thread_data.id


def log_to_file(filename, level=DEBUG):
    """send paramiko logs to a logfile,
    if they're not already going somewhere"""
    logger = logging.getLogger("hwinfo")
    if len(logger.handlers) > 0:
        return
    logger.setLevel(level)
    handler = logging.FileHandler(filename)
    frm = "%(levelname)-.3s [%(asctime)s.%(msecs)03d]"
    frm += " %(name)s: %(message)s"
    handler.setFormatter(logging.Formatter(frm, "%Y%m%d-%H:%M:%S"))
    logger.addHandler(handler)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(frm, "%Y%m%d-%H:%M:%S"))
    logger.addHandler(console)


def logger_add_stream(level = DEBUG):
    logger = logging.getLogger("hwinfo")
    if len(logger.handlers) > 0:
        return
    logger.setLevel(level)
    # handler = logging.FileHandler(filename)
    frm = "%(levelname)-.3s [%(asctime)s.%(msecs)03d]"
    frm += " %(name)s: %(message)s"
    # handler.setFormatter(logging.Formatter(frm, "%Y%m%d-%H:%M:%S"))
    # logger.addHandler(handler)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(frm, "%Y%m%d-%H:%M:%S"))
    logger.addHandler(console)


    # make only one filter object, so it doesn't get applied more than once
class PFilter:
    def filter(self, record):
        record._threadid = get_thread_id()
        return True


_pfilter = PFilter()


def get_logger(name):
    logger = logging.getLogger(name)
    logger.addFilter(_pfilter)
    return logger