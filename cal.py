#!/usr/bin/python3

import subprocess
import sys
import ipaddress
import os
import socket

# Attempt to import requests, install if missing
try:
    import requests
except ImportError:
    print("The 'requests' library is not installed. Installing now...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# ANSI color codes for terminal output
class Colors:
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    HEADER = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

def color_text(text, color):
    return f"{color}{text}{Colors.RESET}"

def print_label(label, value):
    print(f"{color_text(label + ':', Colors.BLUE)} {color_text(value, Colors.WHITE)}")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Full multicast dictionary
MULTICAST_GROUPS = {
    "224.0.0.1": "All hosts on the local subnet",
    "224.0.0.2": "All routers on the local subnet",
    "224.0.0.3": "Unassigned",
    "224.0.0.4": "DVMRP routers",
    "224.0.0.5": "OSPF routers",
    "224.0.0.6": "OSPF designated routers",
    "224.0.0.7": "ST Routers",
    "224.0.0.8": "ST Hosts",
    "224.0.0.9": "RIP version 2 routers",
    "224.0.0.10": "EIGRP Routers",
    "224.0.0.11": "Mobile-Agents",
    "224.0.0.12": "DHCP Server / Relay Agent",
    "224.0.0.13": "All PIM Routers",
    "224.0.0.14": "RSVP-ENCAPSULATION",
    "224.0.0.15": "all-cbt-routers",
    "224.0.0.16": "designated-sbm",
    "224.0.0.17": "all-sbms",
    "224.0.0.18": "VRRP (Virtual Router Redundancy Protocol)",
    "224.0.0.19": "IPAllL1ISs",
    "224.0.0.20": "IPAllL2ISs",
    "224.0.0.21": "IPAllIntermediate Systems",
    "224.0.0.22": "IGMP version 3",
    "224.0.0.23": "GLOBECAST-ID",
    "224.0.0.24": "OSPFIGP-TE",
    "224.0.0.25": "router-to-switch",
    "224.0.0.26": "Unassigned",
    "224.0.0.27": "Al MPP Hello",
    "224.0.0.28": "ETC Control",
    "224.0.0.29": "GE-FANUC",
    "224.0.0.30": "indigo-vhdp",
    "224.0.0.31": "shinbroadband",
    "224.0.0.32": "digistar",
    "224.0.0.33": "ff-system-management",
    "224.0.0.34": "pt2-discover",
    "224.0.0.35": "DXCLUSTER",
    "224.0.0.36": "DTCP Announcement",
    "224.0.0.37": "zeroconfaddr",
    "224.0.0.101": "cisco-nhap",
    "224.0.0.102": "HSRP",
    "224.0.0.103": "MDAP",
    "224.0.0.104": "Nokia MC CH",
    "224.0.0.105": "ff-lr-address",
    "224.0.0.106": "All-Snoopers",
    "224.0.0.107": "PTP-pdelay",
    "224.0.0.108": "Saratoga",
    "224.0.0.109": "LL-MANET-Routers",
    "224.0.0.110": "IGRS",
    "224.0.0.111": "Babel",
    "224.0.0.112": "MMA Device Discovery",
    "224.0.0.113": "AllJoyn",
    "224.0.0.114": "Inter RFID Reader Protocol",
    "224.0.0.115": "JSDP",
    "224.0.0.116": "Device discovery/config",
    "224.0.0.117": "DLEP Discovery",
    "224.0.0.118": "MAAS",
    "224.0.0.119": "ALL_GRASP_NEIGHBORS",
    "224.0.0.120": "3GPP MBMS SACH",
    "224.0.0.121": "ALL_V4_RIFT_ROUTERS",
    "224.0.0.122": "Network Virtualization Overlay (NVO) BUM Traffic",
    "224.0.0.150": "UnasRamp AltitudeCDN MulticastPlussigned",
    "224.0.0.151": "Unassigned",
    "224.0.0.152": "WiseHome",
    "224.0.0.153": "Unassigned",
    "224.0.0.251": "mDNS (Multicast DNS)",
    "224.0.0.252": "Link-local Discovery Protocol (LLDP)",
    "224.0.0.253": "Teredo",
    "224.0.0.254": "RFC3692-style Experiment",
    "224.0.0.255": "Reserved",
    "239.255.255.250": "SSDP (Simple Service Discovery Protocol)",
}

def to_binary(ip):
    return '.'.join(f'{int(octet):08b}' for octet in str(ip).split('.'))

def get_ip_class(ip):
    first_octet = int(str(ip).split('.')[0])
    if 1 <= first_octet <= 126:
        return "A"
    elif 128 <= first_octet <= 191:
        return "B"
    elif 192 <= first_octet <= 223:
        return "C"
    elif 224 <= first_octet <= 239:
        return "D (Multicast)"
    elif 240 <= first_octet <= 254:
        return "E (Experimental)"
    else:
        return "Unknown"

def get_multicast_info(ip):
    ip_str = str(ip)
    if ip_str in MULTICAST_GROUPS:
        return MULTICAST_GROUPS[ip_str]
    try:
        if ipaddress.IPv4Address(ip_str) in ipaddress.IPv4Network("224.0.0.0/24"):
            return "Local Network Control Block"
        elif ipaddress.IPv4Address(ip_str) in ipaddress.IPv4Network("224.0.1.0/24"):
            return "Internetwork Control Block"
        elif ipaddress.IPv4Address(ip_str) in ipaddress.IPv4Network("233.0.0.0/8"):
            return "GLOP addressing (for AS-based multicast)"
        elif ipaddress.IPv4Address(ip_str) in ipaddress.IPv4Network("239.0.0.0/8"):
            return "Administratively Scoped Multicast"
    except Exception:
        pass
    return "Multicast address (unassigned or unknown group)"

def get_ip_info(ip):
    try:
        url = f"https://ipinfo.io/{ip}/json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "asn": data.get("org", "N/A").split()[0][2:] if data.get("org", "").startswith("AS") else "N/A",
                "owner": " ".join(data.get("org", "").split()[1:]) if data.get("org", "").startswith("AS") else data.get("org", "N/A"),
                "country": data.get("country", "N/A"),
                "region": data.get("region", "N/A"),
                "city": data.get("city", "N/A"),
                "location": data.get("loc", "N/A")
            }
    except Exception:
        pass
    return {}

def subnet_calculator():
    while True:
        clear_screen()
        print(color_text("=== Subnet Calculator ===", Colors.HEADER))
        try:
            cidr_input = input(color_text("Enter an IPv4 address with CIDR: ", Colors.CYAN)).strip()
            if "/" not in cidr_input:
                cidr_input += "/32"
            net = ipaddress.ip_network(cidr_input, strict=False)
            ip = ipaddress.ip_address(cidr_input.split("/")[0])

            if get_ip_class(ip).startswith("D"):
                print_label("IP Address", str(ip))
                print_label("Multicast Group", get_multicast_info(ip))
                print_label("Class", get_ip_class(ip))
            else:
                all_hosts = list(net.hosts())
                if len(all_hosts) >= 2:
                    first, last = all_hosts[0], all_hosts[-1]
                elif len(all_hosts) == 1:
                    first = last = all_hosts[0]
                else:
                    first = last = "N/A"

                info = get_ip_info(ip)

                print_label("Network Address", f"{net.network_address}  (Binary: {to_binary(net.network_address)})")
                if isinstance(first, ipaddress.IPv4Address):
                    print_label("First Usable IP", f"{first}  (Binary: {to_binary(first)})")
                    print_label("Last Usable IP", f"{last}  (Binary: {to_binary(last)})")
                else:
                    print_label("First Usable IP", first)
                    print_label("Last Usable IP", last)
                print_label("Broadcast Address", f"{net.broadcast_address}  (Binary: {to_binary(net.broadcast_address)})")
                print_label("Subnet Mask", f"{net.netmask}  (Binary: {to_binary(net.netmask)})")
                print_label("Wildcard Mask", str(ipaddress.IPv4Address(int(net.hostmask))))
                print_label("Total Usable Hosts", str(len(all_hosts)))
                print_label("Class", get_ip_class(ip))
                print_label("Private/Public", "Private" if net.is_private else "Public")

                try:
                    hostname = socket.gethostbyaddr(str(ip))[0]
                except Exception:
                    hostname = "Not found"
                print_label("Hostname", hostname)

                if info:
                    for key, val in info.items():
                        print_label(key.replace('_', ' ').title(), val or "N/A")
        except Exception as e:
            print(color_text(f"Error: {e}", Colors.RED))

        again = input(color_text("\nRun again? (y/n): ", Colors.YELLOW)).lower()
        if again != 'y':
            print(color_text("Goodbye!", Colors.GREEN))
            break

if __name__ == "__main__":
    subnet_calculator()
