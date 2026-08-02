---
type: database_table
title: M_Connection_Category
description: [Add general description of this table's purpose, e.g., Master table storing tariff categories and connection category details for consumers.]
database: mdms_master
default_alias: mcc
tags: 
- connection category
- tariff
- master table
---

## Table Information

[Add business context here: e.g., This lookup table classifies consumers into different tariff buckets and categories used for billing and reporting purposes.]

## Schema

* `ConnectionCategory_TblRefID` (int) : [Add description]
* `Tariff_Category` (varchar) : [Add description]
* `ConnectionCategory_Code` (varchar) : [Add description]
* `ConnectionCategory_Name` (varchar) : [Add description]
* `ConnectionCategory_Desc` (varchar) : [Add description]
* `ConnectionCategory_RAPDRPCode` (varchar) : [Add description]
* `Category_TblRefID` (int) : [Add description]
* `ConTypeTblRefId` (int) : [Add description]
* `TariffTypeTblRefID` (tinyint) : [Add description]
* `HES` (varchar) : [Add description]
* `IsActiveStatus` (bit, Enum: `0`='False', `1`='True') : [Add description]

## Joins

* Joined with [l_consumer_lookup](l_consumer_lookup.md) (alias: `lcl`) ON `mcc.ConnectionCategory_TblRefID` = `lcl.ConnectionCategory_TblRefID`

*(Note: If `ConTypeTblRefId` or `TariffTypeTblRefID` connect to other master tables like `M_ConnectionType`, you can add those explicit JOIN rules here later!)*