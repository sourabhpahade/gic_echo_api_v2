---
type: Table
title: m_paymenttype_contract
description: Master lookup table defining the payment contract types (Prepaid vs. Postpaid) for consumers.
database: mdms_master
default_alias: mptc
tags: 
- payment contract
- prepaid
- postpaid
- payment mode
---

# Table: m_paymenttype_contract

## Description
This master lookup table defines the available payment contract types for consumers. It is primarily used to distinguish between Prepaid and Postpaid accounts across the system.

## Columns
* **PaymentContract_TblRefID** (int, Enum: `1`='Postpaid', `2`='Prepaid'): PRIMARY KEY. Unique identifier for the payment contract type.
* **PaymentContract_Name** (varchar, Enum: `Postpaid`, `Prepaid`): The descriptive name of the payment contract.