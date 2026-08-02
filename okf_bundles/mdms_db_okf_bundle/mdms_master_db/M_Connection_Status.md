---
type: database_table
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

## Table Information

[Add business context here: e.g., This is a lookup table used to map integer status codes to human-readable connection states like "Connected", "Disconnected", or "Permanently Disconnected".]

## Schema

* `ConnectionStatus_TblRefID` (smallint) : [Add description]
* `ConnectionStatus_Name` (varchar) : [Add description]
* `IsActive` (bit, Enum: `0`='False', `1`='True') : [Add description]
* `ShortName` (varchar) : [Add description]

## Joins

* Joined with [l_consumer_lookup](l_consumer_lookup.md) (alias: `lcl`) ON `mcs.ConnectionStatus_TblRefID` = `lcl.ConnectionStatus_TblRefID`
* Joined with [l_consumer_lookup](l_consumer_lookup.md) (alias: `lcl`) ON `mcs.ConnectionStatus_TblRefID` = `lcl.accntstatus_tblrefid`