---
type: Table
title: m_connection_status
description: Master lookup table defining the physical connectivity states of smart meters (e.g., Connected, Disconnected).
database: mdms_master
default_alias: mcs
tags: 
- connection status
- active
- disconnected
- state
---

# Table: m_connection_status

## Description
This master lookup table defines the available connectivity statuses for a consumer's smart meter. It is used to filter consumers who are currently receiving power versus those who have been temporarily or permanently disconnected.

## Columns
* **ConnectionStatus_TblRefID** (smallint, Enum: `1`='Connected', `2`='Disconnected', `3`='Permanent Disconnection'): PRIMARY KEY. Unique identifier for the connectivity state.
* **ConnectionStatus_Name** (varchar, Enum: `Connected`, `Disconnected`, `Permanent Disconnection`): The full descriptive name of the connectivity state.