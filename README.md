# hwinfo User Manual V01
# 1. 支持OS
- [√] Centos 7/8
- [√] Debian 9/10
---
# 2. 依赖关系
如需要获取GPU Information 需要先安装GPU Driver， 安装步骤如下
1. 如果OS带图形界面需init 3，切换到文本界面安装
2. 运行命令`./NVIDIA-Linux-x86_64-xxx.xx.xx.run --no-opengl-files` 选择默认选项
3. 确认`nvidia-smi`命令可执行即表示安装成功

# 3. 使用方法
1. 将hwinfo工具拷贝到Linux OS下
2. 获取使用帮助信息`./hwinfo -h` 
```[root@simonlinux dist]# ./hwinfo -h
usage: hwinfo [-format] [-options ...]

optional arguments:
  -h, --help            show this help message and exit
  -V, -v                show program's version number and exit

  format can be

  -json                 output hardware tree as a JSON object
  -txt                  output hardware tree as txt

  opions can be

  -class {server,mlb,cpu,mem,psu,raid,net,hdd,ssd,nvme,gpu} [{server,mlb,cpu,mem,psu,raid,net,hdd,ssd,nvme,gpu} ...]
                        only show a certain class of hardware
  -log LOG              set script output log to file
  -quiet                don't display status
  -dump DUMP            save hardware tree to a file
  ```
  3. 获取所有硬件信息
  ```

[root@simonlinux dist]# ./hwinfo
INF [20240917-18:50:12.024] hwinfo: ================================================================================
INF [20240917-18:50:12.025] hwinfo.server: #server information
INF [20240917-18:50:12.150] hwinfo.server:
+---------------------------------------------------------------------------+
|                             server Information                            |
+--------------+----------+---------------+--------------+-------+----------+
| Manufacturer |  Model   | ProductNumber | SerialNumber | Suite | Assettag |
+--------------+----------+---------------+--------------+-------+----------+
|   Inventec   | RM761-IV |  WC2214051001 | CKTC39AJ025  |  None |          |
+--------------+----------+---------------+--------------+-------+----------+
INF [20240917-18:50:12.150] hwinfo:
INF [20240917-18:50:12.150] hwinfo: ================================================================================
INF [20240917-18:50:12.151] hwinfo.mlb: #MLB information
INF [20240917-18:50:12.416] hwinfo.mlb:
+---------------------------------------------------------------------------------------------------------------------+
|                                                   MLB Information                                                   |
+----------+----------+-------------------+------+--------------+-------------+--------------+---------+--------------+
|   BIOS   |   BMC    |      BMC_MAC      | CPLD |  PartNumber  | ProductName | SerialNumber | Version | Manufacturer |
+----------+----------+-------------------+------+--------------+-------------+--------------+---------+--------------+
| K888Q234 | 02.43.00 | 38:68:dd:51:fe:0e | None | 1395T3013703 |    ARBOK    |  AR16PP1059  |   None  |   Inventec   |
+----------+----------+-------------------+------+--------------+-------------+--------------+---------+--------------+
INF [20240917-18:50:12.416] hwinfo:
INF [20240917-18:50:12.416] hwinfo: ================================================================================
INF [20240917-18:50:12.416] hwinfo.cpu: #cpu information
INF [20240917-18:50:12.423] hwinfo.cpu:
+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                      CPU Information                                                                      |
+--------+----------------------+--------------------------------------------+------------------+-------------+-----------------+------------+--------------+
| Socket |     Manufacturer     |                   Model                    |       PPIN       | MaxSpeedMHz | CurrentSpeedMHz | TotalCores | TotalThreads |
+--------+----------------------+--------------------------------------------+------------------+-------------+-----------------+------------+--------------+
|  CPU0  | Intel(R) Corporation | Intel(R) Xeon(R) Silver 4208 CPU @ 2.10GHz | 56060500FFFBEBBF |   4000 MHz  |     2100 MHz    |     8      |      16      |
|  CPU1  | Intel(R) Corporation | Intel(R) Xeon(R) Silver 4208 CPU @ 2.10GHz | 56060500FFFBEBBF |   4000 MHz  |     2100 MHz    |     8      |      16      |
+--------+----------------------+--------------------------------------------+------------------+-------------+-----------------+------------+--------------+
INF [20240917-18:50:12.423] hwinfo:
INF [20240917-18:50:12.423] hwinfo: ================================================================================
INF [20240917-18:50:12.423] hwinfo.dram: #dram information
INF [20240917-18:50:12.433] hwinfo.dram:
+-----------------------------------------------------------------------------------------------------------------------------------+
|                                                          DIMM Information                                                         |
+----------+--------------+------------------+--------------------+----------+----------------+------------+------------+-----------+
| Location | Manufacturer |    PartNumber    |    SerialNumber    | Capacity | OperatingSpeed | RatedSpeed | DeviceType | RankCount |
+----------+--------------+------------------+--------------------+----------+----------------+------------+------------+-----------+
| CPU0_D0  |   Samsung    | M393A4K40BB2-CTD | S00DA1080538327DB4 |  32 GB   |   2400 MT/s    | 2666 MT/s  |    DDR4    |     2     |
+----------+--------------+------------------+--------------------+----------+----------------+------------+------------+-----------+
INF [20240917-18:50:12.433] hwinfo:
INF [20240917-18:50:12.433] hwinfo: ================================================================================
INF [20240917-18:50:12.433] hwinfo.psu: #psu information
INF [20240917-18:50:13.034] hwinfo.psu:
+------------------------------------------------------------------------------+
|                               PSU Information                                |
+----------+--------------+------------+-----------------+----------+----------+
| Location | Manufacturer |   Model    |   SerialNumber  | Firmware | MaxPower |
+----------+--------------+------------+-----------------+----------+----------+
|   PSU1   |    Liteon    | PS-2801-9L | 60CWN0103K042D7 | 00.06.09 |   800W   |
|   PSU2   |    Liteon    | PS-2801-9L | 60CWN0105M019NE | 00.06.09 |   800W   |
+----------+--------------+------------+-----------------+----------+----------+
INF [20240917-18:50:13.034] hwinfo:
INF [20240917-18:50:13.034] hwinfo: ================================================================================
INF [20240917-18:50:13.034] hwinfo.hba: #hba(raid) information
DEB [20240917-18:50:13.090] hwinfo.hba: FOUND 1 CARDS
INF [20240917-18:50:13.092] hwinfo.hba:
+----------------------------------------------------------------------------------------------------+
|                                          HBA Information                                           |
+----------------------+----------+------------+------------+--------------+--------------+----------+
|         Type         | Firmware |    BIOS    | BIOS Date  |    PCI id    | Firmware Rev | MPT Rev  |
+----------------------+----------+------------+------------+--------------+--------------+----------+
| LSI Logic SAS3008 C0 | 16.00.10 | 8.37.00.00 | 2018.04.04 | 0000:5e:00:0 |     205      | 10000a00 |
+----------------------+----------+------------+------------+--------------+--------------+----------+
INF [20240917-18:50:13.092] hwinfo:
INF [20240917-18:50:13.092] hwinfo: ================================================================================
INF [20240917-18:50:13.092] hwinfo.nic: #nic information
INF [20240917-18:50:13.414] hwinfo.nic:
+------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                 NIC Controler Information                                                                  |
+--------------+--------------+----------------------------------------+------+------------+--------------+--------------------------+-----------+-----------+
|     Bus      | Manufacturer |                 Model                  | Type | PartNumber | Serialnumber |         Firmware         | LinkSpeed | LinkWidth |
+--------------+--------------+----------------------------------------+------+------------+--------------+--------------------------+-----------+-----------+
| 0000:3d:00.1 |    Intel     | Ethernet Connection X722 for 10GBASE-T | PCIe |    None    |     None     | 4.10 0x80001a64 1.2585.0 |  2.5GT/s  |     x1    |
| 0000:3d:00.0 |    Intel     | Ethernet Connection X722 for 10GBASE-T | PCIe |    None    |     None     | 4.10 0x80001a64 1.2585.0 |  2.5GT/s  |     x1    |
+--------------+--------------+----------------------------------------+------+------------+--------------+--------------------------+-----------+-----------+
INF [20240917-18:50:13.415] hwinfo.nic:
+-----------------------------------------------------------------------------------------------------------+
|                                            NICPort Information                                            |
+--------------+-----------+-------------------+----------+--------+---------------+-----------+------------+
|      ID      |  PortName |      MacAddr      |  Speed   | Driver | DriverVersion | MediaType | LinkStatus |
+--------------+-----------+-------------------+----------+--------+---------------+-----------+------------+
| 0000:3d:00.1 | enp61s0f1 | 38:68:dd:51:fe:0d | 1000Mb/s |  i40e  |    2.3.2-k    |    None   |    yes     |
| 0000:3d:00.0 | enp61s0f0 | 38:68:dd:51:fe:0c | 1000Mb/s |  i40e  |    2.3.2-k    |    None   |    yes     |
+--------------+-----------+-------------------+----------+--------+---------------+-----------+------------+
INF [20240917-18:50:13.415] hwinfo:
INF [20240917-18:50:13.415] hwinfo: ================================================================================
INF [20240917-18:50:13.416] hwinfo.hdd: #hdd information
INF [20240917-18:50:14.073] hwinfo.hdd:
+-----------------------------------------------------------------------------------------------------+
|                                           HDD Information                                           |
+---------+--------------+---------------------+--------------+---------+----------+------+-----------+
| Logical | Manufacturer |        Model        | SerialNumber |   Size  | Firmware | RPM  | LinkSpeed |
+---------+--------------+---------------------+--------------+---------+----------+------+-----------+
|   sda   |   Seagate    | ST8000AS0002-1NA17Z |   Z84047X7   | 8.00 TB |   AR15   | 5980 |  6.0 Gb/s |
+---------+--------------+---------------------+--------------+---------+----------+------+-----------+
INF [20240917-18:50:14.073] hwinfo:
INF [20240917-18:50:14.073] hwinfo: ================================================================================
INF [20240917-18:50:14.073] hwinfo.ssd: #ssd information
INF [20240917-18:50:14.089] hwinfo:
INF [20240917-18:50:14.089] hwinfo: ================================================================================
INF [20240917-18:50:14.089] hwinfo.nvme: #nvme information
INF [20240917-18:50:14.090] hwinfo:
INF [20240917-18:50:14.090] hwinfo: ================================================================================
INF [20240917-18:50:14.090] hwinfo.gpu: #gpu information
INF [20240917-18:50:14.134] hwinfo.gpu: Not Found GPU
INF [20240917-18:50:14.135] hwinfo:
```
4. 获取单个或多个类型信息
```
root@SUT1:~# ./hwinfo -c net nvme
INF [20190217-22:02:09.643] hwinfo: ================================================================================
INF [20190217-22:02:09.643] hwinfo.nic: #nic information
INF [20190217-22:02:09.903] hwinfo.nic:
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                        NIC Controler Information                                                                        |
+--------------+--------------+-------------------------------+------+----------------------------+------------------+----------------------------+-----------+-----------+
|     Bus      | Manufacturer |             Model             | Type |         PartNumber         |   Serialnumber   |          Firmware          | LinkSpeed | LinkWidth |
+--------------+--------------+-------------------------------+------+----------------------------+------------------+----------------------------+-----------+-----------+
| 0000:31:00.0 |   Mellanox   | MT2892 Family [ConnectX-6 Dx] | OCP  |  MCX623430MS-CDAB          |  MT23494001V1    | 22.35.3502 (MT_0000000774) |   16GT/s  |    x16    |
| 0000:31:00.1 |   Mellanox   | MT2892 Family [ConnectX-6 Dx] | OCP  |  MCX623430MS-CDAB          |  MT23494001V1    | 22.35.3502 (MT_0000000774) |   16GT/s  |    x16    |
|   2-1:1.0    |     None     |              None             | USB  |            None            |       None       |                            |    None   |    None   |
+--------------+--------------+-------------------------------+------+----------------------------+------------------+----------------------------+-----------+-----------+
INF [20190217-22:02:09.906] hwinfo.nic:
+----------------------------------------------------------------------------------------------------------------------------+
|                                                    NICPort Information                                                     |
+--------------+-----------------+-------------------+----------+--------------+--------------------+-----------+------------+
|      ID      |     PortName    |      MacAddr      |  Speed   |    Driver    |   DriverVersion    | MediaType | LinkStatus |
+--------------+-----------------+-------------------+----------+--------------+--------------------+-----------+------------+
| 0000:31:00.0 |    ens5f0np0    | 58:a2:e1:26:b9:c4 | Unknown! |  mlx5_core   | 5.15.120-usbdebug+ |    None   |     no     |
| 0000:31:00.1 |    ens5f1np1    | 58:a2:e1:26:b9:c5 | Unknown! |  mlx5_core   | 5.15.120-usbdebug+ |    None   |     no     |
|   2-1:1.0    | enxf8e43bf1493d | f8:e4:3b:f1:49:3d | 1000Mb/s | ax88179_178a | 5.15.120-usbdebug+ |    None   |    yes     |
+--------------+-----------------+-------------------+----------+--------------+--------------------+-----------+------------+
INF [20190217-22:02:09.906] hwinfo:
INF [20190217-22:02:09.906] hwinfo: ================================================================================
INF [20190217-22:02:09.906] hwinfo.nvme: #nvme information
INF [20190217-22:02:09.977] hwinfo.nvme:
+--------------------------------------------------------------------------------------------------------------------------+
|                                                     NVMe Information                                                     |
+------------+--------------+----------------------------+----------------+----------+----------+-----------+--------------+
|    dev     | manufacturer |           model            |  serialnumber  | capacity | firmware | numa_node |     bdf      |
+------------+--------------+----------------------------+----------------+----------+----------+-----------+--------------+
| /dev/nvme0 |   SAMSUNG    | SAMSUNG MZQL27T6HBLA-00B7C | S6CVNE0R906652 | 7.68 TB  | GDC56C2Q |     0     | 0000:4b:00.0 |
+------------+--------------+----------------------------+----------------+----------+----------+-----------+--------------+
INF [20190217-22:02:09.977] hwinfo:
```
5. 输入为json format
```
[root@simonlinux dist]# ./hwinfo -json
INF [20240917-18:51:32.509] hwinfo.server: #server information
INF [20240917-18:51:32.643] hwinfo.mlb: #MLB information
INF [20240917-18:51:32.897] hwinfo.cpu: #cpu information
INF [20240917-18:51:32.904] hwinfo.dram: #dram information
INF [20240917-18:51:32.914] hwinfo.psu: #psu information
INF [20240917-18:51:33.583] hwinfo.hba: #hba(raid) information
DEB [20240917-18:51:33.641] hwinfo.hba: FOUND 1 CARDS
INF [20240917-18:51:33.642] hwinfo.nic: #nic information
INF [20240917-18:51:33.995] hwinfo.hdd: #hdd information
INF [20240917-18:51:34.363] hwinfo.ssd: #ssd information
INF [20240917-18:51:34.379] hwinfo.nvme: #nvme information
INF [20240917-18:51:34.379] hwinfo.gpu: #gpu information
INF [20240917-18:51:34.427] hwinfo.gpu: Not Found GPU
INF [20240917-18:51:34.427] hwinfo: {
    "server": {
        "Manufacturer": "Inventec",
        "Model": "RM761-IV",
        "ProductNumber": "WC2214051001",
        "SerialNumber": "CKTC39AJ025",
        "Suite": null,
        "Assettag": ""
    },
    "mlb": {
        "BIOS": "K888Q234",
        "BMC": "02.43.00",
        "BMC_MAC": "38:68:dd:51:fe:0e",
        "CPLD": null,
        "PartNumber": "1395T3013703",
        "ProductName": "ARBOK",
        "SerialNumber": "AR16PP1059",
        "Version": null,
        "Manufacturer": "Inventec"
    },
    "cpu": {
        "Maximum": 2,
        "details": [
            {
                "Socket": "CPU0",
                "Manufacturer": "Intel(R) Corporation",
                "Model": "Intel(R) Xeon(R) Silver 4208 CPU @ 2.10GHz",
                "PPIN": "56060500FFFBEBBF",
                "MaxSpeedMHz": "4000 MHz",
                "CurrentSpeedMHz": "2100 MHz",
                "TotalCores": "8",
                "TotalThreads": "16"
            },
            {
                "Socket": "CPU1",
                "Manufacturer": "Intel(R) Corporation",
                "Model": "Intel(R) Xeon(R) Silver 4208 CPU @ 2.10GHz",
                "PPIN": "56060500FFFBEBBF",
                "MaxSpeedMHz": "4000 MHz",
                "CurrentSpeedMHz": "2100 MHz",
                "TotalCores": "8",
                "TotalThreads": "16"
            }
        ]
    },
    "mem": {
        "Maximum": 1,
        "DRAM_TOP": "000000100000000000000000",
        "TotalSystemMemorySize[GiB]": 32,
        "details": [
            {
                "Location": "CPU0_D0",
                "Manufacturer": "Samsung",
                "PartNumber": "M393A4K40BB2-CTD",
                "SerialNumber": "S00DA1080538327DB4",
                "Capacity": "32 GB",
                "OperatingSpeed": "2400 MT/s",
                "RatedSpeed": "2666 MT/s",
                "DeviceType": "DDR4",
                "RankCount": "2"
            }
        ]
    },
    "psu": [
        {
            "Location": "PSU1",
            "Manufacturer": "Liteon",
            "Model": "PS-2801-9L",
            "SerialNumber": "60CWN0103K042D7",
            "Firmware": "00.06.09",
            "MaxPower": "800W"
        },
        {
            "Location": "PSU2",
            "Manufacturer": "Liteon",
            "Model": "PS-2801-9L",
            "SerialNumber": "60CWN0105M019NE",
            "Firmware": "00.06.09",
            "MaxPower": "800W"
        }
    ],
    "raid": [
        {
            "Type": "LSI Logic SAS3008 C0",
            "Firmware": "16.00.10",
            "BIOS": "8.37.00.00",
            "BIOS Date": "2018.04.04",
            "PCI id": "0000:5e:00:0",
            "Firmware Rev": "205",
            "MPT Rev": "10000a00"
        }
    ],
    "net": [
        {
            "Bus": "0000:3d:00.1",
            "DEVID": "8086:37d2",
            "SYSID": "1170:37d2",
            "Manufacturer": "Intel",
            "Model": "Ethernet Connection X722 for 10GBASE-T",
            "Type": "PCIe",
            "PartNumber": null,
            "Serialnumber": null,
            "Firmware": "4.10 0x80001a64 1.2585.0",
            "LinkSpeed": "2.5GT/s",
            "LinkWidth": "x1",
            "Port": {
                "ID": "0000:3d:00.1",
                "PortName": "enp61s0f1",
                "MacAddr": "38:68:dd:51:fe:0d",
                "Speed": "1000Mb/s",
                "Driver": "i40e",
                "DriverVersion": "2.3.2-k",
                "MediaType": null,
                "LinkStatus": "yes"
            }
        },
        {
            "Bus": "0000:3d:00.0",
            "DEVID": "8086:37d2",
            "SYSID": "1170:37d2",
            "Manufacturer": "Intel",
            "Model": "Ethernet Connection X722 for 10GBASE-T",
            "Type": "PCIe",
            "PartNumber": null,
            "Serialnumber": null,
            "Firmware": "4.10 0x80001a64 1.2585.0",
            "LinkSpeed": "2.5GT/s",
            "LinkWidth": "x1",
            "Port": {
                "ID": "0000:3d:00.0",
                "PortName": "enp61s0f0",
                "MacAddr": "38:68:dd:51:fe:0c",
                "Speed": "1000Mb/s",
                "Driver": "i40e",
                "DriverVersion": "2.3.2-k",
                "MediaType": null,
                "LinkStatus": "yes"
            }
        }
    ],
    "hdd": [
        {
            "Logical": "sda",
            "Manufacturer": "Seagate",
            "Model": "ST8000AS0002-1NA17Z",
            "SerialNumber": "Z84047X7",
            "Size": "8.00 TB",
            "Firmware": "AR15",
            "RPM": 5980,
            "LinkSpeed": "6.0 Gb/s"
        }
    ],
    "ssd": [],
    "nvme": [],
    "gpu": []
}
{
    "server": {
        "Manufacturer": "Inventec",
        "Model": "RM761-IV",
        "ProductNumber": "WC2214051001",
        "SerialNumber": "CKTC39AJ025",
        "Suite": null,
        "Assettag": ""
    },
    "mlb": {
        "BIOS": "K888Q234",
        "BMC": "02.43.00",
        "BMC_MAC": "38:68:dd:51:fe:0e",
        "CPLD": null,
        "PartNumber": "1395T3013703",
        "ProductName": "ARBOK",
        "SerialNumber": "AR16PP1059",
        "Version": null,
        "Manufacturer": "Inventec"
    },
    "cpu": {
        "Maximum": 2,
        "details": [
            {
                "Socket": "CPU0",
                "Manufacturer": "Intel(R) Corporation",
                "Model": "Intel(R) Xeon(R) Silver 4208 CPU @ 2.10GHz",
                "PPIN": "56060500FFFBEBBF",
                "MaxSpeedMHz": "4000 MHz",
                "CurrentSpeedMHz": "2100 MHz",
                "TotalCores": "8",
                "TotalThreads": "16"
            },
            {
                "Socket": "CPU1",
                "Manufacturer": "Intel(R) Corporation",
                "Model": "Intel(R) Xeon(R) Silver 4208 CPU @ 2.10GHz",
                "PPIN": "56060500FFFBEBBF",
                "MaxSpeedMHz": "4000 MHz",
                "CurrentSpeedMHz": "2100 MHz",
                "TotalCores": "8",
                "TotalThreads": "16"
            }
        ]
    },
    "mem": {
        "Maximum": 1,
        "DRAM_TOP": "000000100000000000000000",
        "TotalSystemMemorySize[GiB]": 32,
        "details": [
            {
                "Location": "CPU0_D0",
                "Manufacturer": "Samsung",
                "PartNumber": "M393A4K40BB2-CTD",
                "SerialNumber": "S00DA1080538327DB4",
                "Capacity": "32 GB",
                "OperatingSpeed": "2400 MT/s",
                "RatedSpeed": "2666 MT/s",
                "DeviceType": "DDR4",
                "RankCount": "2"
            }
        ]
    },
    "psu": [
        {
            "Location": "PSU1",
            "Manufacturer": "Liteon",
            "Model": "PS-2801-9L",
            "SerialNumber": "60CWN0103K042D7",
            "Firmware": "00.06.09",
            "MaxPower": "800W"
        },
        {
            "Location": "PSU2",
            "Manufacturer": "Liteon",
            "Model": "PS-2801-9L",
            "SerialNumber": "60CWN0105M019NE",
            "Firmware": "00.06.09",
            "MaxPower": "800W"
        }
    ],
    "raid": [
        {
            "Type": "LSI Logic SAS3008 C0",
            "Firmware": "16.00.10",
            "BIOS": "8.37.00.00",
            "BIOS Date": "2018.04.04",
            "PCI id": "0000:5e:00:0",
            "Firmware Rev": "205",
            "MPT Rev": "10000a00"
        }
    ],
    "net": [
        {
            "Bus": "0000:3d:00.1",
            "DEVID": "8086:37d2",
            "SYSID": "1170:37d2",
            "Manufacturer": "Intel",
            "Model": "Ethernet Connection X722 for 10GBASE-T",
            "Type": "PCIe",
            "PartNumber": null,
            "Serialnumber": null,
            "Firmware": "4.10 0x80001a64 1.2585.0",
            "LinkSpeed": "2.5GT/s",
            "LinkWidth": "x1",
            "Port": {
                "ID": "0000:3d:00.1",
                "PortName": "enp61s0f1",
                "MacAddr": "38:68:dd:51:fe:0d",
                "Speed": "1000Mb/s",
                "Driver": "i40e",
                "DriverVersion": "2.3.2-k",
                "MediaType": null,
                "LinkStatus": "yes"
            }
        },
        {
            "Bus": "0000:3d:00.0",
            "DEVID": "8086:37d2",
            "SYSID": "1170:37d2",
            "Manufacturer": "Intel",
            "Model": "Ethernet Connection X722 for 10GBASE-T",
            "Type": "PCIe",
            "PartNumber": null,
            "Serialnumber": null,
            "Firmware": "4.10 0x80001a64 1.2585.0",
            "LinkSpeed": "2.5GT/s",
            "LinkWidth": "x1",
            "Port": {
                "ID": "0000:3d:00.0",
                "PortName": "enp61s0f0",
                "MacAddr": "38:68:dd:51:fe:0c",
                "Speed": "1000Mb/s",
                "Driver": "i40e",
                "DriverVersion": "2.3.2-k",
                "MediaType": null,
                "LinkStatus": "yes"
            }
        }
    ],
    "hdd": [
        {
            "Logical": "sda",
            "Manufacturer": "Seagate",
            "Model": "ST8000AS0002-1NA17Z",
            "SerialNumber": "Z84047X7",
            "Size": "8.00 TB",
            "Firmware": "AR15",
            "RPM": 5980,
            "LinkSpeed": "6.0 Gb/s"
        }
    ],
    "ssd": [],
    "nvme": [],
    "gpu": []
}
```
6. 将结果保存到文件内
```
[root@simonlinux dist]# ./hwinfo -json -d hwinfo.json
INF [20240917-18:52:56.474] hwinfo.server: #server information
INF [20240917-18:52:56.602] hwinfo.mlb: #MLB information
INF [20240917-18:52:56.868] hwinfo.cpu: #cpu information
INF [20240917-18:52:56.875] hwinfo.dram: #dram information
INF [20240917-18:52:56.885] hwinfo.psu: #psu information
INF [20240917-18:52:57.479] hwinfo.hba: #hba(raid) information
DEB [20240917-18:52:57.536] hwinfo.hba: FOUND 1 CARDS
INF [20240917-18:52:57.537] hwinfo.nic: #nic information
INF [20240917-18:52:57.872] hwinfo.hdd: #hdd information
INF [20240917-18:52:58.245] hwinfo.ssd: #ssd information
INF [20240917-18:52:58.261] hwinfo.nvme: #nvme information
INF [20240917-18:52:58.262] hwinfo.gpu: #gpu information
INF [20240917-18:52:58.308] hwinfo.gpu: Not Found GPU
INF [20240917-18:52:58.309] hwinfo: {
    "server": {
        "Manufacturer": "Inventec",
        "Model": "RM761-IV",
        "ProductNumber": "WC2214051001",
        "SerialNumber": "CKTC39AJ025",
        "Suite": null,
        "Assettag": ""
    },
    "mlb": {
        "BIOS": "K888Q234",
        "BMC": "02.43.00",
        "BMC_MAC": "38:68:dd:51:fe:0e",
        "CPLD": null,
        "PartNumber": "1395T3013703",
        "ProductName": "ARBOK",
        "SerialNumber": "AR16PP1059",
        "Version": null,
        "Manufacturer": "Inventec"
    },
    "cpu": {
        "Maximum": 2,
        "details": [
            {
                "Socket": "CPU0",
                "Manufacturer": "Intel(R) Corporation",
                "Model": "Intel(R) Xeon(R) Silver 4208 CPU @ 2.10GHz",
                "PPIN": "56060500FFFBEBBF",
                "MaxSpeedMHz": "4000 MHz",
                "CurrentSpeedMHz": "2100 MHz",
                "TotalCores": "8",
                "TotalThreads": "16"
            },
            {
                "Socket": "CPU1",
                "Manufacturer": "Intel(R) Corporation",
                "Model": "Intel(R) Xeon(R) Silver 4208 CPU @ 2.10GHz",
                "PPIN": "56060500FFFBEBBF",
                "MaxSpeedMHz": "4000 MHz",
                "CurrentSpeedMHz": "2100 MHz",
                "TotalCores": "8",
                "TotalThreads": "16"
            }
        ]
    },
    "mem": {
        "Maximum": 1,
        "DRAM_TOP": "000000100000000000000000",
        "TotalSystemMemorySize[GiB]": 32,
        "details": [
            {
                "Location": "CPU0_D0",
                "Manufacturer": "Samsung",
                "PartNumber": "M393A4K40BB2-CTD",
                "SerialNumber": "S00DA1080538327DB4",
                "Capacity": "32 GB",
                "OperatingSpeed": "2400 MT/s",
                "RatedSpeed": "2666 MT/s",
                "DeviceType": "DDR4",
                "RankCount": "2"
            }
        ]
    },
    "psu": [
        {
            "Location": "PSU1",
            "Manufacturer": "Liteon",
            "Model": "PS-2801-9L",
            "SerialNumber": "60CWN0103K042D7",
            "Firmware": "00.06.09",
            "MaxPower": "800W"
        },
        {
            "Location": "PSU2",
            "Manufacturer": "Liteon",
            "Model": "PS-2801-9L",
            "SerialNumber": "60CWN0105M019NE",
            "Firmware": "00.06.09",
            "MaxPower": "800W"
        }
    ],
    "raid": [
        {
            "Type": "LSI Logic SAS3008 C0",
            "Firmware": "16.00.10",
            "BIOS": "8.37.00.00",
            "BIOS Date": "2018.04.04",
            "PCI id": "0000:5e:00:0",
            "Firmware Rev": "205",
            "MPT Rev": "10000a00"
        }
    ],
    "net": [
        {
            "Bus": "0000:3d:00.1",
            "DEVID": "8086:37d2",
            "SYSID": "1170:37d2",
            "Manufacturer": "Intel",
            "Model": "Ethernet Connection X722 for 10GBASE-T",
            "Type": "PCIe",
            "PartNumber": null,
            "Serialnumber": null,
            "Firmware": "4.10 0x80001a64 1.2585.0",
            "LinkSpeed": "2.5GT/s",
            "LinkWidth": "x1",
            "Port": {
                "ID": "0000:3d:00.1",
                "PortName": "enp61s0f1",
                "MacAddr": "38:68:dd:51:fe:0d",
                "Speed": "1000Mb/s",
                "Driver": "i40e",
                "DriverVersion": "2.3.2-k",
                "MediaType": null,
                "LinkStatus": "yes"
            }
        },
        {
            "Bus": "0000:3d:00.0",
            "DEVID": "8086:37d2",
            "SYSID": "1170:37d2",
            "Manufacturer": "Intel",
            "Model": "Ethernet Connection X722 for 10GBASE-T",
            "Type": "PCIe",
            "PartNumber": null,
            "Serialnumber": null,
            "Firmware": "4.10 0x80001a64 1.2585.0",
            "LinkSpeed": "2.5GT/s",
            "LinkWidth": "x1",
            "Port": {
                "ID": "0000:3d:00.0",
                "PortName": "enp61s0f0",
                "MacAddr": "38:68:dd:51:fe:0c",
                "Speed": "1000Mb/s",
                "Driver": "i40e",
                "DriverVersion": "2.3.2-k",
                "MediaType": null,
                "LinkStatus": "yes"
            }
        }
    ],
    "hdd": [
        {
            "Logical": "sda",
            "Manufacturer": "Seagate",
            "Model": "ST8000AS0002-1NA17Z",
            "SerialNumber": "Z84047X7",
            "Size": "8.00 TB",
            "Firmware": "AR15",
            "RPM": 5980,
            "LinkSpeed": "6.0 Gb/s"
        }
    ],
    "ssd": [],
    "nvme": [],
    "gpu": []
}
{
    "server": {
        "Manufacturer": "Inventec",
        "Model": "RM761-IV",
        "ProductNumber": "WC2214051001",
        "SerialNumber": "CKTC39AJ025",
        "Suite": null,
        "Assettag": ""
    },
    "mlb": {
        "BIOS": "K888Q234",
        "BMC": "02.43.00",
        "BMC_MAC": "38:68:dd:51:fe:0e",
        "CPLD": null,
        "PartNumber": "1395T3013703",
        "ProductName": "ARBOK",
        "SerialNumber": "AR16PP1059",
        "Version": null,
        "Manufacturer": "Inventec"
    },
    "cpu": {
        "Maximum": 2,
        "details": [
            {
                "Socket": "CPU0",
                "Manufacturer": "Intel(R) Corporation",
                "Model": "Intel(R) Xeon(R) Silver 4208 CPU @ 2.10GHz",
                "PPIN": "56060500FFFBEBBF",
                "MaxSpeedMHz": "4000 MHz",
                "CurrentSpeedMHz": "2100 MHz",
                "TotalCores": "8",
                "TotalThreads": "16"
            },
            {
                "Socket": "CPU1",
                "Manufacturer": "Intel(R) Corporation",
                "Model": "Intel(R) Xeon(R) Silver 4208 CPU @ 2.10GHz",
                "PPIN": "56060500FFFBEBBF",
                "MaxSpeedMHz": "4000 MHz",
                "CurrentSpeedMHz": "2100 MHz",
                "TotalCores": "8",
                "TotalThreads": "16"
            }
        ]
    },
    "mem": {
        "Maximum": 1,
        "DRAM_TOP": "000000100000000000000000",
        "TotalSystemMemorySize[GiB]": 32,
        "details": [
            {
                "Location": "CPU0_D0",
                "Manufacturer": "Samsung",
                "PartNumber": "M393A4K40BB2-CTD",
                "SerialNumber": "S00DA1080538327DB4",
                "Capacity": "32 GB",
                "OperatingSpeed": "2400 MT/s",
                "RatedSpeed": "2666 MT/s",
                "DeviceType": "DDR4",
                "RankCount": "2"
            }
        ]
    },
    "psu": [
        {
            "Location": "PSU1",
            "Manufacturer": "Liteon",
            "Model": "PS-2801-9L",
            "SerialNumber": "60CWN0103K042D7",
            "Firmware": "00.06.09",
            "MaxPower": "800W"
        },
        {
            "Location": "PSU2",
            "Manufacturer": "Liteon",
            "Model": "PS-2801-9L",
            "SerialNumber": "60CWN0105M019NE",
            "Firmware": "00.06.09",
            "MaxPower": "800W"
        }
    ],
    "raid": [
        {
            "Type": "LSI Logic SAS3008 C0",
            "Firmware": "16.00.10",
            "BIOS": "8.37.00.00",
            "BIOS Date": "2018.04.04",
            "PCI id": "0000:5e:00:0",
            "Firmware Rev": "205",
            "MPT Rev": "10000a00"
        }
    ],
    "net": [
        {
            "Bus": "0000:3d:00.1",
            "DEVID": "8086:37d2",
            "SYSID": "1170:37d2",
            "Manufacturer": "Intel",
            "Model": "Ethernet Connection X722 for 10GBASE-T",
            "Type": "PCIe",
            "PartNumber": null,
            "Serialnumber": null,
            "Firmware": "4.10 0x80001a64 1.2585.0",
            "LinkSpeed": "2.5GT/s",
            "LinkWidth": "x1",
            "Port": {
                "ID": "0000:3d:00.1",
                "PortName": "enp61s0f1",
                "MacAddr": "38:68:dd:51:fe:0d",
                "Speed": "1000Mb/s",
                "Driver": "i40e",
                "DriverVersion": "2.3.2-k",
                "MediaType": null,
                "LinkStatus": "yes"
            }
        },
        {
            "Bus": "0000:3d:00.0",
            "DEVID": "8086:37d2",
            "SYSID": "1170:37d2",
            "Manufacturer": "Intel",
            "Model": "Ethernet Connection X722 for 10GBASE-T",
            "Type": "PCIe",
            "PartNumber": null,
            "Serialnumber": null,
            "Firmware": "4.10 0x80001a64 1.2585.0",
            "LinkSpeed": "2.5GT/s",
            "LinkWidth": "x1",
            "Port": {
                "ID": "0000:3d:00.0",
                "PortName": "enp61s0f0",
                "MacAddr": "38:68:dd:51:fe:0c",
                "Speed": "1000Mb/s",
                "Driver": "i40e",
                "DriverVersion": "2.3.2-k",
                "MediaType": null,
                "LinkStatus": "yes"
            }
        }
    ],
    "hdd": [
        {
            "Logical": "sda",
            "Manufacturer": "Seagate",
            "Model": "ST8000AS0002-1NA17Z",
            "SerialNumber": "Z84047X7",
            "Size": "8.00 TB",
            "Firmware": "AR15",
            "RPM": 5980,
            "LinkSpeed": "6.0 Gb/s"
        }
    ],
    "ssd": [],
    "nvme": [],
    "gpu": []
}
[root@simonlinux dist]# ls hwinfo.json
hwinfo.json
[root@simonlinux dist]#

```