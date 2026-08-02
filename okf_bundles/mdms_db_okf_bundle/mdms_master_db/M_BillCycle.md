---
type: database_table
title: M_BillCycle
description: [Add general description of this table's purpose, e.g., Master table storing the different billing cycles assigned to consumers.]
database: mdms_master
default_alias: mbc
tags: 
- bill cycle
- billing
- master table
---

## Table Information

[Add business context here: e.g., This table defines the billing frequencies (such as monthly, quarterly, or yearly) that dictate when a consumer's bill is generated in the MDMS system.]

## Schema

* `billcycleTblRefiID` (int) : [Add description]
* `billcycle` (varchar) : [Add description]
* `IsActive` (bit, Enum: `0`='False', `1`='True') : [Add description]
* `EntryLoginCode` (int) : [Add description or mark as internal]
* `EntryDateTime` (datetime) : [Add description or mark as internal]
* `UpdateLoginCode` (int) : [Add description or mark as internal]
* `UpdateDateTime` (datetime) : [Add description or mark as internal]

## Joins

* Joined with [l_consumer_lookup](l_consumer_lookup.md) (alias: `lcl`) ON `mbc.billcycleTblRefiID` = `lcl.BillcycleTblRefiID`