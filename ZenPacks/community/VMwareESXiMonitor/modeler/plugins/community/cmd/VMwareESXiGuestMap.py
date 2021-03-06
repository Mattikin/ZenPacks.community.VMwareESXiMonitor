################################################################################
#
# This program is part of the VMwareESXiMonitor Zenpack for Zenoss.
# Copyright (C) 2014 Eric Enns, Matthias Kittl.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__ = """VMwareESXiGuestMap

VMwareESXiGuestMap gathers ESXi Guest information.

"""

import re, commands, os
import Globals
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap

class VMwareESXiGuestMap(PythonPlugin):
    maptype = 'VMwareESXiGuestMap'
    relname = "esxiVm"
    modname = 'ZenPacks.community.VMwareESXiMonitor.ESXiVM'
    deviceProperties = PythonPlugin.deviceProperties + (
        'zVSphereUsername',
        'zVSpherePassword'
    )

    def collect(self, device, log):
        log.info('Getting VMware ESXi guest info for device %s' % device.id)
        cmd = os.path.abspath('%s/../../../../libexec/esxi_guestinfo.pl' % os.path.dirname(__file__))
        username = getattr(device, 'zVSphereUsername', None)
        password = getattr(device, 'zVSpherePassword', None)
        if (not username or not password):
            return None
        (stat, results) = commands.getstatusoutput( "/usr/bin/perl %s --server %s --username %s --password '%s'" % (cmd, device.id, username, password))
        if (stat != 0):
            return None
        else:
            return results

    def process(self, device, results, log):
        log.info('Processing VMware ESXi guest info for device %s' % device.id)
        rm = self.relMap()
        rlines = results.split("\n")
        for line in rlines:
            if line.startswith("Warning:"):
                log.warning('%s' % line)
            elif re.search(';', line):
                name, memSize, os = line.split(';')
                rm.append(self.objectMap({
                    'id': self.prepId(name),
                    'title': name,
                    'osType': os,
                    'memory': int(memSize) * 1024 * 1024,
                }))
        log.debug(rm)

        return rm

