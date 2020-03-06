#!/usr/bin/python

#  Copyright 2019-present Open Networking Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import argparse

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo

from bmv2 import ONOSStratumSwitch
from host6 import IPv6Host

CPU_PORT = 255


class TutorialTopo(Topo):
    """
                 transit_r1 -- transit_r3
                /           \ /          \ 
    end_r1 -----             \            ----- end-r2
                \           / \          /
                 transit_r2 -- transit_r4
    """

    def __init__(self, *args, **kwargs):
        Topo.__init__(self, *args, **kwargs)

        # End routers
        end_r1 = self.addSwitch('end_r1', cls=ONOSStratumSwitch, grpcport=50001,
                               cpuport=CPU_PORT)
        end_r2 = self.addSwitch('end_r2', cls=ONOSStratumSwitch, grpcport=50002,
                               cpuport=CPU_PORT)

        # Transit routers
        transit_r1 = self.addSwitch('transit_r1', cls=ONOSStratumSwitch, grpcport=50011,
                                cpuport=CPU_PORT)
        transit_r2 = self.addSwitch('transit_r2', cls=ONOSStratumSwitch, grpcport=50012,
                                cpuport=CPU_PORT)
        transit_r3 = self.addSwitch('transit_r3', cls=ONOSStratumSwitch, grpcport=50013,
                                cpuport=CPU_PORT)
        transit_r4 = self.addSwitch('transit_r4', cls=ONOSStratumSwitch, grpcport=50014,
                                cpuport=CPU_PORT)
        
        # Switch Links
        self.addLink(end_r1, transit_r1)
        self.addLink(end_r1, transit_r2)
        
        self.addLink(transit_r1, transit_r3)
        self.addLink(transit_r1, transit_r4) 
        self.addLink(transit_r2, transit_r3)
        self.addLink(transit_r2, transit_r4)        
        
        self.addLink(transit_r3, end_r2) 
        self.addLink(transit_r4, end_r2)
       
        
        # IPv6 hosts attached to leaf 1
        h1 = self.addHost('h1', cls=IPv6Host, mac="00:00:00:00:00:10",
                           ipv6='2001:1:1::1/64', ipv6_gw='2001:1:1::ff')
        h2 = self.addHost('h2', cls=IPv6Host, mac="00:00:00:00:00:20",
                          ipv6='2001:1:2::1/64', ipv6_gw='2001:1:2::ff')

        self.addLink(h1, end_r1)
        self.addLink(h2, end_r2)


def main(argz):
    topo = TutorialTopo()
    controller = RemoteController('c0', ip=argz.onos_ip)

    net = Mininet(topo=topo, controller=None)
    net.addController(controller)

    net.start()
    CLI(net)
    net.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Mininet script for cisco-srv6 topology')
    parser.add_argument('--onos-ip', help='ONOS controller IP address',
                        type=str, action="store", required=True)
    args = parser.parse_args()
    setLogLevel('info')

    main(args)
