---
type: Table
title: M_Connection_Status
description: [Add general description of this table's purpose, e.g., Master table defining the various connection and relay statuses for consumer meters.]
database: mdms_master
default_alias: mcs
tags: 
- connection status
- master table
- connect
- disconnect
---

# Table: M_Connection_Status

## Description
[Add business context here: e.g., This is a lookup table used to map integer status codes to human-readable connection states like "Connected", "Disconnected", or "Permanently Disconnected".]

## Columns
* **ConnectionStatus_TblRefID** (smallint): [Add description]
* **ConnectionStatus_Name** (varchar): [Add description]
* **IsActive** (bit, Enum: `0`='False', `1`='True'): [Add description]
* **ShortName** (varchar): [Add description]
