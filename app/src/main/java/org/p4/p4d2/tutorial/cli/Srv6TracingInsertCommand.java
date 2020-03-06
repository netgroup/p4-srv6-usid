/*
 * Copyright 2019-present Open Networking Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.p4.p4d2.tutorial.cli;

import org.apache.karaf.shell.api.action.Argument;
import org.apache.karaf.shell.api.action.Command;
import org.apache.karaf.shell.api.action.Completion;
import org.apache.karaf.shell.api.action.lifecycle.Service;
import org.onlab.packet.Ip6Address;
import org.onlab.packet.IpAddress;
import org.onosproject.cli.AbstractShellCommand;
import org.onosproject.cli.net.DeviceIdCompleter;
import org.onosproject.net.Device;
import org.onosproject.net.DeviceId;
import org.onosproject.net.device.DeviceService;
import org.p4.p4d2.tutorial.Srv6Component;

/**
 * SRv6 Transit Insert Command
 */
@Service
@Command(scope = "onos", name = "srv6-tracing-insert",
         description = "Insert a tracing insert rule into the SRv6 Tracing table")
public class Srv6TracingInsertCommand extends AbstractShellCommand {

    @Argument(index = 0, name = "uri", description = "Device ID",
              required = true, multiValued = false)
    @Completion(DeviceIdCompleter.class)
    String uri = null;

    @Argument(index = 1, name = "dstAddress",
            description = "SRv6 Segments (space separated list); last segment is target IP address",
            required = false, multiValued = false)
    String dstAddress = null;

    @Argument(index = 2, name = "mask",
            description = "IPv6 mask",
            required = false, multiValued = false)
    int mask = 128;

    @Override
    protected void doExecute() {
        DeviceService deviceService = get(DeviceService.class);
        Srv6Component app = get(Srv6Component.class);

        Device device = deviceService.getDevice(DeviceId.deviceId(uri));
        if (device == null) {
            print("Device \"%s\" is not found", uri);
            return;
        }
        
        Ip6Address destIp = Ip6Address.valueOf(dstAddress);

        print("Installing add tracing list command on device %s", uri);

        app.insertSrv6TracingInsertRule(device.id(), destIp, mask);

    }

}
