---
type: Table
title: m_connection_category
description: Master lookup table defining the tariff and connection categorization for consumers (e.g., Domestic, Commercial, Agriculture).
database: mdms_master
default_alias: mcc
tags: 
- tariff
- commercial
- residential
- category
- connection category
---

# Table: m_connection_category

## Description
This master lookup table defines the specific tariff codes and categorizations applied to consumers. It acts as the source of truth for classifying connections into business groups such as Domestic, Commercial, Agriculture, and Industrial.

## Columns
* **ConnectionCategory_TblRefID** (int, Enum: `1`='KJ', `2`='KJ_BPL_MTR', `3`='DS1', `4`='DS1D', `5`='DS2D', `6`='DS3D', `7`='NDS1', `8`='NDS-IID(A)', `9`='NDS2D', `10`='LTIS1D', `11`='LTIS2D', `12`='IAS1', `13`='IAS2', `14`='PWWD', `15`='HGN', `16`='SS1D', `17`='LTEV', `18`='NDS1D', `19`='IAS2D'): PRIMARY KEY. Unique identifier for the connection category.
* **ConnectionCategory_Code** (varchar): UNIQUE. The standard shorthand code for the connection category (matches the ID enums).
* **ConnectionCategory_Desc** (varchar, Enum: `Kuteer Jyoti`, `Domestic`, `Commercial`, `LT Industrial`, `Agriculture`, `Public Water Works`, `Har Ghar Nal`, `Street Light`, `EV Charging`): The full descriptive name and classification of the connection category.