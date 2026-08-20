---
type: Table
title: M_Connection_Category
description: [Add general description of this table's purpose, e.g., Master table storing tariff categories and connection category details for consumers.]
database: mdms_master
default_alias: mcc
tags: 
- connection category
- tariff
- master table
---

# Table: M_Connection_Category

## Description
[Add business context here: e.g., This lookup table classifies consumers into different tariff buckets and categories used for billing and reporting purposes.]

## Columns
* **ConnectionCategory_TblRefID** (int): [Add description]
* **Tariff_Category** (varchar): [Add description]
* **ConnectionCategory_Code** (varchar): [Add description]
* **ConnectionCategory_Name** (varchar): [Add description]
* **ConnectionCategory_Desc** (varchar): [Add description]
* **ConnectionCategory_RAPDRPCode** (varchar): [Add description]
* **Category_TblRefID** (int): [Add description]
* **ConTypeTblRefId** (int): [Add description]
* **TariffTypeTblRefID** (tinyint): [Add description]
* **HES** (varchar): [Add description]
* **IsActiveStatus** (bit, Enum: `0`='False', `1`='True'): [Add description]
