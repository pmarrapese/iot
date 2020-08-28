#!/usr/bin/python3
#
# Copyright (c) 2020, Paul A. Marrapese <paul@redprocyon.com>
# All rights reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS 
# SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE 
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES 
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, 
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.

import os, logging, socket, re
from netifaces import interfaces, ifaddresses, AF_INET

LOG_LEVEL = logging.DEBUG if 'DEBUG' in os.environ and os.environ['DEBUG'] else logging.INFO
logging.basicConfig(format='%(message)s', level=LOG_LEVEL)

P2P_LAN_BROADCAST_IP = '255.255.255.255'
P2P_LAN_PORT = 32108
P2P_MAGIC_NUM = 0xF1
P2P_HEADER_SIZE = 4
MSG_LAN_SEARCH = 0x30
MSG_LAN_SEARCH_EXT = 0x32
MSG_PUNCH_PKT = 0x41
YUNNI_CHECK_CODE_PATTERN = re.compile('[A-F]{5}')
VSTARCAM_PREFIXES = ['VSTD', 'VSTF', 'QHSV', 'EEEE', 'ROSS', 'ISRP', 'GCMN', 'ELSA']

def fetchLocalIPv4Addresses():
  ret = []
  ifaces = interfaces()
  for iface in ifaces:
    addrs = ifaddresses(iface)
    if AF_INET in addrs: addrs = addrs[AF_INET]
    else: continue
      
    for addr in addrs:
      ip = addr['addr']
      if ip in ret or ip == '0.0.0.0' or ip == '127.0.0.1' or ip[0:7] == '169.254': continue
      ret.append(ip)
    
  return ret
  
class Device:
  def __init__(self, prefix, serial, checkCode):
    self.prefix = prefix
    self.serial = serial
    self.checkCode = checkCode
    self.isYunniDevice = prefix in VSTARCAM_PREFIXES or YUNNI_CHECK_CODE_PATTERN.match(checkCode)
    self.uid = '%s-%s-%s' % (self.prefix, str(self.serial).zfill(6), self.checkCode)
  
class P2PClient:
  def __init__(self):
    self.devices = {}
    
  def tryLANSearch(self, sourceIp):
    logging.debug('Starting LAN search from IP: %s' % (sourceIp))
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(.5)
    s.bind((sourceIp, 0))
    
    lanSearch = self.createP2PMessage(MSG_LAN_SEARCH)
    lanSearchExt = self.createP2PMessage(MSG_LAN_SEARCH_EXT)
    s.sendto(lanSearch, (P2P_LAN_BROADCAST_IP, P2P_LAN_PORT))
    s.sendto(lanSearchExt, (P2P_LAN_BROADCAST_IP, P2P_LAN_PORT))
    
    # parse responses until the socket times out
    while True:     
      try:
        (buff, rinfo) = s.recvfrom(1024)
        logging.debug('Data from %s: %s' % (rinfo, buff))
        
        try:
          device = self.parsePunchPkt(buff)
        except Exception as e:
          logging.error('Failed to parse P2P message (%s): %s' % (e, buff))
          continue
        
        if device.uid in self.devices: 
          continue
          
        device.ip = rinfo[0]
        self.devices[device.uid] = device

        if device.isYunniDevice:
          # the 'EEEE' prefix is used by both Yunni and CS2, but the check code makes it impossible to distinguish
          if device.prefix == 'EEEE': judgement = 'CS2 Network P2P or iLnkP2P'
          else: judgement = 'iLnkP2P'
        else: judgement = 'CS2 Network P2P'
        
        logging.info('===================================================\n'
                     '[*] Found %s device %s at %s\n' 
                     '===================================================\n'
                      % (judgement, device.uid, device.ip)
                    )
      except socket.timeout as e:
        return
    
  def parsePunchPkt(self, buff):
    if len(buff) < 4 or buff[0] != P2P_MAGIC_NUM:
      raise Exception('Invalid P2P message')
      
    msgType = buff[1]
    if msgType == MSG_PUNCH_PKT:
      prefix = buff[4:12].decode('ascii').rstrip('\0')
      serial = int.from_bytes(buff[12:16], 'big')
      checkCode = buff[16:22].decode('ascii').rstrip('\0')
      
      return Device(prefix, serial, checkCode)
    else:
      raise Exception('Unexpected P2P message')

  def createP2PMessage(self, type, payload = bytes(0)):
    payloadSize = len(payload)
    buff = bytearray(P2P_HEADER_SIZE + payloadSize)
    buff[0] = P2P_MAGIC_NUM
    buff[1] = type
    buff[2:4] = payloadSize.to_bytes(2, 'big')
    buff[4:] = payload
    return buff

def main():
  logging.info('[*] P2P LAN Search v1.1\n'
               '[*] Copyright (c) 2020, Paul A. Marrapese <paul@redprocyon.com>\n'
               '[*] Searching for P2P devices...\n')
  client = P2PClient()
  ips = fetchLocalIPv4Addresses()

  for ip in ips:
    try:
      client.tryLANSearch(ip)
    except Exception as e:
      logging.error('LAN search failed on adapter %s: %s' % (ip, e))

  if len(client.devices) == 0:
    logging.info('[*] No devices found.')
  logging.info('[*] Done.')

if __name__ == "__main__":
  main()