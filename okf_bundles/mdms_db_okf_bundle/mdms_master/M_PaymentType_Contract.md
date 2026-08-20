---
type: Table
title: M_PaymentType_Contract
description: [Add general description of this table's purpose, e.g., Master table defining the payment modes or contract types for consumers.]
database: mdms_master
default_alias: mptc
tags: 
- payment contract
- prepaid
- postpaid
- master table
---

# Table: M_PaymentType_Contract

## Description
[Add business context here: e.g., This lookup table specifies whether a consumer is on a prepaid or postpaid payment contract.]

## Columns
* **PaymentContract_TblRefID** (int): [Add description]
* **PaymentContract_Code** (varchar): [Add description]
* **PaymentContract_Name** (varchar): [Add description]
* **IsActiveStatus** (bit, Enum: `0`='False', `1`='True'): [Add description]
