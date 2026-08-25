---
type: Table
title: m_servicepoint_meterphase
description: Master lookup table defining the phase configurations of smart meters (e.g., 1 Phase, 3 Phase).
database: mdms_master
default_alias: msmp
tags: 
- meter phase
- 1 phase
- 3 phase
- ht
---

# Table: m_servicepoint_meterphase

## Description
This master lookup table defines the available physical phase configurations and connection types for smart meters across the system. It helps differentiate between standard single-phase residential meters, three-phase commercial/industrial meters, and High Tension (HT) connections.

## Columns
* **ServicePointMeterPhase_TblRefID** (int, Enum: `1`='1 PH', `2`='3PH WC', `3`='3PH LT CT', `4`='HT', `6`='3PH LT CT'): PRIMARY KEY. Unique identifier for the meter phase configuration.
* **MeterPhase_Name** (varchar, Enum: `1 PH`, `3PH WC`, `3PH LT CT`, `HT`): The standard descriptive name of the meter phase.
* **IsActive** (bit, Enum: `0`='No', `1`='Yes'): Indicates whether this phase configuration is currently active in the system.