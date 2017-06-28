# -*- coding: utf-8 -*-
import scapy
from scapy.all import *

from scapy.all import conf

# from scapy.all import sniff
# from scapy.all import wrpcap

# print  IP()

dpkt  = sniff(iface = "wlp7s0", count = 100)

print dpkt
# wrpcap("demo.pcap", dpkt)
