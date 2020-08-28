# P2P LAN Search
Python script to find devices on the local network that use CS2 Network P2P and Shenzhen Yunni iLnkP2P.

This will broadcast "LAN search" messages on each IPv4 network the machine is connected to. P2P devices listen for these
messages on UDP port 32108, and will respond with their UID.  

## Prerequisites
Requires Python 3 and the `netifaces` library (`pip3 install netifaces`)

## Usage
**Note:** You may need to temporarily disable your computer's firewall for this to work.

Invoke with `python3 lansearch.py`