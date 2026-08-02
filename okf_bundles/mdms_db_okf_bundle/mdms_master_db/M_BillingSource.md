---
type: database_table
title: M_BillingSource
description: [Add general description of this table's purpose, e.g., Master table storing the source systems or entities responsible for consumer billing.]
database: mdms_master
default_alias: mbs
tags: 
- billing source
- master table
---

## Table Information

[Add business context here: e.g., This lookup table defines where the consumer's billing data originates or which system handles the generation of their bills.]

## Schema

* `BillingSource_TblRefID` (int) : [Add description]
* `BillingSource_Name` (nvarchar) : [Add description]
* `IsActive` (int, Enum: `0`='False', `1`='True') : [Add description]

## Joins

* Joined with [l_consumer_lookup](l_consumer_lookup.md) (alias: `lcl`) ON `mbs.BillingSource_TblRefID` = `lcl.BillingSource_TblRefID`