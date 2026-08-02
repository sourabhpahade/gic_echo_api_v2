---
type: database_table
title: M_ConnectionType
description: [Add general description of this table's purpose, e.g., Master table storing the different connection types for consumers.]
database: mdms_master
default_alias: mct
tags: 
- connection type
- master table
- connect
- disconnect
---

## Table Information

[Add business context here: e.g., This lookup table defines the nature of the consumer's connection, such as normal, government, temporary, or permanent.]

## Schema

* `ConnectionTypeTblRefID` (int) : [Add description]
* `ConnectionType_Name` (varchar) : [Add description]
* `IsActive` (bit, Enum: `0`='False', `1`='True') : [Add description]

## Joins

* Joined with [l_consumer_lookup](l_consumer_lookup.md) (alias: `lcl`) ON `mct.ConnectionTypeTblRefID` = `lcl.ConnectionTypeTblRefID`