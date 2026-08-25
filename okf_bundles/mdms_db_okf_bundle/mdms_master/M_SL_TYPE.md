---
type: Table
title: m_sl_type
description: Master lookup table defining the units of measurement for sanctioned load and contract demand (e.g., KW, KVA, HP).
database: mdms_master
default_alias: mslt
tags: 
- sanctioned load
- load unit
- kw
- kva
- hp
- watt
---

# Table: m_sl_type

## Description
This master lookup table defines the units of electrical power measurement used to represent a consumer's Sanctioned Load or Contract Demand. It ensures standardized calculations across different connection types.

## Columns
* **SL_TYPE_ID** (smallint, Enum: `1`='KW', `2`='KVA', `3`='HP', `4`='W'): PRIMARY KEY. Unique identifier for the sanctioned load unit of measurement.
* **SL_TYPE_NAME** (varchar, Enum: `KW`, `KVA`, `HP`, `W`): The standard abbreviation/name of the electrical power unit.