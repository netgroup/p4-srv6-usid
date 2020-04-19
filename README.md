# SRv6 uSID (micro SID) implementation on P4

This repository hosts the Srv6 uSID (i.e. micro SID) implementation on P4 and features a DEMO using:
- mininet for network emulation;
- behavioral-model-v2 (bmv2) for the software implementation of the P4 datapath;
- onos to control the P4 enabled switches.

This is the [project web page](https://netgroup.github.io/p4-srv6-usid/), part of the [ROSE](https://netgroup.github.io/rose/) project.

This demo is based on the P4 tutorial by Open Networking Foundation. As such, it is possible to find more information about the above listed software modules in their [repository](https://github.com/opennetworkinglab/onos-p4-tutorial). There you can also find useful material like the slides explaining the tutorial and a prepared Ubuntu 18 virtual machine with all the software installed. It is strongly recommended to download the prepared VM and run the DEMO inside it, as it contains the several dependencies needed to run the software.

In the following, we will present only the steps needed to run the SRv6 micro SID demo, starting from the downloaded VM.

## Repository structure

This repository is structured as follows:

 * `p4src/` P4 implementation
 * `app/` ONOS app Java implementation
 * `mininet/` Mininet script to emulate a topology of `stratum_bmv2` devices
 * `config/` configuration files
 * `docs/` documentation

## DEMO overview

In this demo we illustrate the use-case of transporting customer packets over a SRv6 network from Site A to Site B forcing the packets to cross two waypoints (nodes R8 and R7) along the path from node R1 to node R2. Regular shortest path routing is used from R1 to R8, from R8 to R7 and from R7 to R2.

For a complete description of the proposed use-case please refer to the 
SRv6 "Micro program" [video tutorial](http://www.segment-routing.net/20200212-srv6-status/srv6-technology-and-use-cases-part5) available on the
[Segment Routing website](http://www.segment-routing.net/)

<!--- img source (old version in draw.io):
      https://drive.google.com/file/d/1vMB6GEX-DhCClDEddQC_Ss_MY_HNiwAq/view?usp=sharing --->
<!--- img source (new version in gslide):
      https://docs.google.com/presentation/d/1rV0ViQYk9lYUnJH16zvf5qBDUK4yTWAeHoryo6Fe0jo/edit#slide=id.g7f4100c2bd_6_0 
      export the slide as .png, cut to roughly 615x341, and upload in docs/images with the same name --->
![p4-srv6-usid-demo-topology.jpg](<./docs/images/p4-srv6-usid-demo-topology.png>)

The demo runs on a mininet topology made up of eight P4 enabled switches (based on [bmv2](https://github.com/p4lang/behavioral-model) P4 software implementation) and two hosts that represent Site A and Site B. For this demo we rely on static routing for simplicity.

The Onos controller is used to configure the P4 software switches with the various table entries, e.g. IPv6 routes, L2 forwarding entries, SRv6 micro-instructions , etc.
Onos works as a service in which you can instantiate the applications using the ONOS SDK.

## DEMO commands

To ease the execution of the commands needed to setup the required software, we make use of the Makefile prepared by the ONF for their [P4 tutorial](https://github.com/opennetworkinglab/onos-p4-tutorial).

| Make command        | Description                                            |
|---------------------|------------------------------------------------------- |
| `make p4`           | Builds the P4 program                                  |
| `make onos-run`     | Runs ONOS on the current terminal window               |
| `make onos-cli`     | Access the ONOS command line interface (CLI)           |
| `make app-build`    | Builds the tutorial app and pipeconf                   |
| `make app-reload`   | Load the app in ONOS                                   |
| `make topo`         | Starts the Mininet topology                            |
| `make netcfg`       | Pushes netcfg.json file (network config) to ONOS       |
| `make reset`        | Resets the tutorial environment                        |
| `make onos-upgrade` | Upgrades the ONOS version                              |

## Detailed DEMO description

### 1. Start ONOS

In a terminal window, start the ONOS main process by running:

```bash
$> make onos-run
```

It will take some time until all the onos JAVA modules get loaded. The process is finished when the onos process displays the following message:

```bash
INFO  [AtomixClusterStore] Updated node 127.0.0.1 state to READ
```
### 2. Build and load the application

An application is provided to ONOS as an executable in .oar format. To build the source code contained in `app/` issue the following command:

```bash
$> make app-build
```

This will create the `srv6-uSID-1.0-SNAPSHOT.oar` application binary in the `app/target/` folder.

Moreover, it will compile the p4 code contained in `p4src` creating two output files:

- `bmv2.json` is the JSON description of the dataplane programmed in P4;
- `p4info.txt` contains the information about the southbound interface used by the controller to program the switches.

These two files are symlinked inside the `app/src/main/resources/` folder and used to build the application.

After the creation of the binary, we have to load it inside ONOS:

```bash
$> make app-reload
```

The app should now be registered in ONOS.

### 3. Start mininet

Now we can actually start the P4 switches with mininet:

```bash
$> make topo
```

This command will run the python script `mininet/topo.py` and setup the mininet topology with custom P4 switches and IPv6 enabled hosts.

### 4. Push the network configuration to ONOS

ONOS gets its global network view thanks to a JSON configuration file in which it is possible to encode several information about the switch configuraton. This file is parsed at runtime by the application and it is needed to configure, e.g. the MAC addresses, SID and uSID addresses assigned to each P4 switch.

Let's push it to ONOS by prompting the following command:

```bash
$> make netcfg
```

Now ONOS knows how to connect to the switches set up in mininet.

### 5. Insert the SRv6 micro SID routing directives

In a new window open the ONOS CLI with the following command:

```bash
$> make onos-cli
```

For the purpose of this DEMO, we statically configured the IPv6 routes of each router inside a .txt file consisting on a list of `route-insert` commands. Configure them inside the switches by sourcing this file inside the CLI:

```bash
onos-cli> source path/to/p4-srv6-usid/route_commands.txt
```

Then, we can insert the uSID routing directive to the the two end routers, one for the path H1 ---> H2 and one for the reverse path H2 ---> H1:

```bash
onos-cli> srv6-insert device:r1 fcbb:bbbb:08:07:02:: 2001:1:2::1
onos-cli> srv6-insert device:r2 fcbb:bbbb:03:06:07:08:05:04 fcbb:bbbb:01:: 2001:1:1::1
```

Essentially, these commands specify to the end routers (R1 and R2) to insert an SRv6 header with a list of SIDs. The first represents the list of uSID that the packet must traverse while the last is the IPv6 address of the host the packet is destined to. In this case the uSID paths would be:

* H1 ---> R1 ---> R8 ---> R7 ---> R2 ---> H2
* H2 ---> R2 ---> R3 ---> R6 ---> R7 ---> R8 ---> R5 ---> R4 ---> R1 ---> H1

### 6. Test

Test the communication between the two hosts with ping inside mininet.

```bash
mininet> h2 ping h1
mininet> h1 ping h2
```

The first pings will not work since the switch will not know how to reach the host at L2 layer. After learning on both paths it will work.

It is also possible to have a graphical representation of the running topology thanks to the ONOS web UI. Type in a browser `localhost:8181/onos/ui` and enter as user `onos` with password `rocks`. It will display the graphical representation of the topology.

Now, let's make some faster pings:

```bash
mininet> h1 ping h2 -i 0.1
```

Then, return to the UI and press
* `h` to show the hosts
* `l` to display the nodes labels
* `a` a few times until it displays link utilization in packets per second

If all was configured right, the result should look like this:

![onos-ui-topo.png](<./docs/images/onos-ui-topo.png>)
