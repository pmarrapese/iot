# P2P Wireshark Dissector

Dissector for the "PPPP" protocol, as used by CS2 Network P2P and Shenzhen Yunni iLnkP2P.

## Installation

1. Download the appropriate version of the [Wireshark Generic Dissector](http://wsgd.free.fr/download.html) plugin for your version of Wireshark
2. Copy `generic.dll` to the desired plugin directory
   (see [WSGD installation](http://wsgd.free.fr/installation.html), e.g. `C:\Users\<username>\AppData\Roaming\Wireshark\plugins\3.2\epan`)
3. Copy `pppp.wsgd` (protocol file) and `pppp.fdesc` (data format description file) to the desired directory
   (see [WSGD installation](http://wsgd.free.fr/installation.html), e.g., `C:\Users\<username>\AppData\Roaming\Wireshark\profiles`)
