---
type: Table
title: l_network_lookup
description: Core table storing the physical electrical network hierarchy, including Substations, Feeders, and DTRs, and mapping them to organizations.
database: mdms_master
default_alias: lnl
tags: 
- network
- substation
- feeder
- dtr
- hierarchy
---

# Table: l_network_lookup

## Description
This table contains the records for all electrical network entities (such as Substations, Feeders, and Distribution Transformer (DTR) networks). It defines the strict physical hierarchy of the grid, including how lower-level networks connect to higher-level networks and which utility organizations manage them.

## Columns
* **NetworkLookup_TblRefID** (int): PRIMARY KEY. Unique internal identity number for each network entity.
* **Network_Code** (varchar): Standard identifier code for the network.
* **Network_RAPDRPCode** (varchar): RAPDRP-specific identifier code for the network.
* **Network_Name** (nvarchar): Name of the network entity.
* **Network_Address** (nvarchar): Physical address or location of the network entity.
* **HigherNetwork_ID** (int): FOREIGN KEY to `l_network_lookup` (Self-referencing). Maps the network to its parent or higher-level network entity.
* **NetworkHierarchy_TblRefID** (int, Enum: `1`='substation', `2`='feeder', `3`='dtr'): FOREIGN KEY to `m_network_hierarchy`. Defines the type of network and its level in the physical hierarchy.
* **OrganisationLookup_TblRefID** (int): FOREIGN KEY to `l_organisation_lookup`. Maps the network to the specific organization or office that manages it.
* **IsActiveStatus** (bit, Enum: `0`='No', `1`='Yes'): Indicates if the network entity is currently active.
* **SUPPLY_VTG_TblRefID** (int, Enum: `1`='11kv', `2`='33kv'): Stores the supply voltage capacity for the network.