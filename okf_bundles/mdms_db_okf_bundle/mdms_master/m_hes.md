---
type: Table
title: m_hes
description: Master lookup table defining the Head-End Systems (HES) responsible for collecting data from smart meters.
database: mdms_master
default_alias: mhes
tags: 
- hes
- head end system
- meter communication
- data collection
---

# Table: m_hes

## Description
This master lookup table defines the various Head-End Systems (HES) integrated into the MDMS. The HES is the central software that communicates directly with the smart meters to collect readings and push configurations.

## Columns
* **HESID** (smallint, Enum: `1`='Scaler', `2`='LT AMR', `3`='HT AMR', `4`='HES-Cyan', `5`='Esya', `6`='HES-BCITs', `7`='HES-Genus', `8`='Crystal-2', `9`='LnG', `10`='Schneider-HES', `11`='Genus-HES', `12`='Genus-HES2', `13`='Ashoka-HES', `14`='BCITS- HES2', `15`='Ashoka-HES2'): PRIMARY KEY. Unique identifier for the Head-End System.
* **HESNAME** (varchar): The descriptive name of the Head-End System software or vendor.
* **IsActiveStatus** (bit, Enum: `0`='No', `1`='Yes'): Indicates whether this Head-End System is currently active and supported in the environment.