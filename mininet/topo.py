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
    /--------\   /----\   /----\   /----\   /----\
    | Site A |---| R1 |---| R4 |---| R5 |---| R8 |
    \________/   \____/   \____/   \____/   \____/
                   |         |       |        |
                   |         |       |        |
    /--------\   /----\   /----\   /----\   /----\
    | Site B |---| R2 |---| R3 |---| R6 |---| R7 |
    \________/   \____/   \____/   \____/   \____/

    """


    def __init__(self, *args, **kwargs):
        Topo.__init__(self, *args, **kwargs)

        # End routers
        r1 = self.addSwitch('r1', cls=ONOSStratumSwitch, grpcport=50001,
                               cpuport=CPU_PORT)
        r2 = self.addSwitch('r2', cls=ONOSStratumSwitch, grpcport=50002,
                               cpuport=CPU_PORT)

        # Transit routers
        r3 = self.addSwitch('r3', cls=ONOSStratumSwitch, grpcport=50003,
                                cpuport=CPU_PORT)
        r4 = self.addSwitch('r4', cls=ONOSStratumSwitch, grpcport=50004,
                                cpuport=CPU_PORT)
        r5 = self.addSwitch('r5', cls=ONOSStratumSwitch, grpcport=50005,
                                cpuport=CPU_PORT)
        r6 = self.addSwitch('r6', cls=ONOSStratumSwitch, grpcport=50006,
                                cpuport=CPU_PORT)
        r7 = self.addSwitch('r7', cls=ONOSStratumSwitch, grpcport=50007,
                                cpuport=CPU_PORT)
        r8 = self.addSwitch('r8', cls=ONOSStratumSwitch, grpcport=50008,
                                cpuport=CPU_PORT)
        

        # Switch Links
        self.addLink(r1, r2)
        self.addLink(r1, r4)

        self.addLink(r2, r3)

        self.addLink(r4, r5)
        self.addLink(r4, r3)

        self.addLink(r3, r6)

        self.addLink(r5, r8)
        self.addLink(r5, r6)

        self.addLink(r6, r7)

        self.addLink(r7, r8)

        # IPv6 hosts attached to leaf 1
        h1 = self.addHost('h1', cls=IPv6Host, mac="00:00:00:00:00:10",
                           ipv6='2001:1:1::1/64', ipv6_gw='2001:1:1::ff')
        h2 = self.addHost('h2', cls=IPv6Host, mac="00:00:00:00:00:20",
                          ipv6='2001:1:2::1/64', ipv6_gw='2001:1:2::ff')

        self.addLink(h1, r1)
        self.addLink(h2, r2)


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
