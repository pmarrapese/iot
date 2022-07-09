# P2P Wireshark Dissector Changelog

## v0.3 (2022-07-08)
### Added
- Added versioning and changelog
- Added CS2 V4 messages `MSG_DEV_LGN_DSK`, `MSG_P2P_REQ_DSK`, `MSG_LIST_REQ_DSK`, and `MSG_REPORT_SESSION_READY`
- Added comments to denote messages from different protocol versions/forks
### Fixed
- Removed incorrect fields from `MSG_DEV_LGN_ACK` and `MSG_DEV_LGN_ACK_CRC`


## v0.2 (2020-08-28)
### Fixed
- Fixed `MSG_PSR` not being dissected


## v0.1 (2020-07-31)
Initial release