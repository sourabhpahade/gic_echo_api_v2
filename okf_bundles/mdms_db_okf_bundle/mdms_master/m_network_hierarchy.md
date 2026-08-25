---
type: Table
title: m_network_hierarchy
description: Master lookup table defining the levels of the physical electrical network hierarchy (e.g., Sub Station, Feeder, DTR).
database: mdms_master
default_alias: mnh
tags: 
- network hierarchy
- substation
- feeder
- dtr
---

# Table: m_network_hierarchy

## Description
This master lookup table defines the specific tiers within the electrical grid's physical hierarchy. It is used to categorize network entities into top-level Substations, mid-level Feeders, and edge-level Distribution Transformers (DTRs).

## Columns
* **NetworkHierarchy_TblRefID** (int, Enum: `1`='Sub Station', `2`='Feeder', `3`='DTR'): PRIMARY KEY. Unique identifier for the network hierarchy level.
* **NetworkHierarchy_Code** (varchar): Standard numeric code representing the hierarchy level.
* **NetworkHierarchy_Name** (nvarchar, Enum: `Sub Station`, `Feeder`, `DTR`): The descriptive name of the network tier.
* **IsActiveStatus** (bit, Enum: `0`='No', `1`='Yes'): Indicates whether this network hierarchy level is currently active in the system.