---
type: database_table
title: M_SL_TYPE
description: [Add general description of this table's purpose, e.g., Master table storing the units of measurement for a consumer's sanctioned load.]
database: mdms_master
default_alias: msl
tags: 
- sanctioned load
- units
- master table
---

## Table Information

[Add business context here: e.g., This lookup table defines the specific unit types used for power measurements, such as kW (kilowatts), kVA (kilovolt-amperes), or HP (horsepower).]

## Schema

* `SL_TYPE_ID` (smallint) : [Add description]
* `SL_TYPE_NAME` (varchar) : [Add description]

## Joins

* Joined with [l_consumer_lookup](l_consumer_lookup.md) (alias: `lcl`) ON `msl.SL_TYPE_ID` = `lcl.SL_TYPE_ID`