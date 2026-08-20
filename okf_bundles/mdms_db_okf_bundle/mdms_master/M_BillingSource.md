---
type: Table
title: M_BillingSource
description: [Add general description of this table's purpose, e.g., Master table storing the source systems or entities responsible for consumer billing.]
database: mdms_master
default_alias: mbs
tags: 
- billing source
- master table
---

# Table: M_BillingSource

## Description
[Add business context here: e.g., This lookup table defines where the consumer's billing data originates or which system handles the generation of their bills.]

## Columns
* **BillingSource_TblRefID** (int): [Add description]
* **BillingSource_Name** (nvarchar): [Add description]
* **IsActive** (int, Enum: `0`='False', `1`='True'): [Add description]
