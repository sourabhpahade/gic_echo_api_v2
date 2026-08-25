---
type: DatabaseIndex
title: MDMS Master Database
description: Core operational database for MDMS consumer, meter, network, and organizational data.
database_alias: mdms_master
---

# MDMS Master Database Index

This database handles the core operational data for smart meter installations, consumer details, utility hierarchies, and the master lookup tables that define system statuses and categories.

## Navigation Guide for Agents
1. Start here or in the root bundle index.
2. Always consult `relationships.md` before writing multi-table SQL.
3. Only join tables that appear in the documented joins.

## Core Operational Tables
These are the primary transaction and entity tables. Note that Network and Organisation tables contain self-referencing hierarchy keys.

* **[Consumer Lookup](mdms_master/l_consumer_lookup.md)**
  * *Description:* Core consumer profiles, connectivity statuses, tariff categories, and installation timestamps.
  * *Keywords:* consumer, rrnumber, account.
* **[Meter Lookup](mdms_master/l_meter_lookup.md)**
  * *Description:* Smart meter hardware details, physical properties, manufacturers, and logical mappings to networks/consumers/ organisation.
  * *Keywords:* meter, smart meter.
* **[Organisation Lookup](mdms_master/l_organisation_lookup.md)**
  * *Description:* Utility office hierarchy (HQ, Circle, Division, etc.) with self-referencing parent-child structure.
  * *Keywords:* organisation, hierarchy, office, division, section.
* **[Network Lookup](mdms_master/l_network_lookup.md)**
  * *Description:* Physical electrical grid hierarchy (Substation, Feeder, DTR) with self-referencing parent-child structure.
  * *Keywords:* network, substation, feeder, dtr, hierarchy.

## Master Tables (Lookups)
These tables define the enums, categories, and configurations used by the core operational tables:

* **[Connection Status](mdms_master/M_Connection_Status.md)**
  * *Description:* Defines physical connectivity (Connected, Disconnected, Permanent Disconnection).
* **[Connection Category](mdms_master/M_Connection_Category.md)**
  * *Description:* Tariff and connection categorization (Domestic, Commercial, Agriculture, etc.).
* **[Payment Type Contract](mdms_master/M_PaymentType_Contract.md)**
  * *Description:* Payment modes (Prepaid vs. Postpaid).
* **[Sanctioned Load Type](mdms_master/M_SL_TYPE.md)**
  * *Description:* Units of measurement for electrical power (KW, KVA, HP, W).
* **[Device Manufacturer](mdms_master/M_Device_Manufacturer.md)**
  * *Description:* Complete list of authorized smart meter brands and manufacturers (L&T, Genus, Secure, etc.).
* **[HES](mdms_master/M_HES.md)**
  * *Description:* Head-End Systems responsible for smart meter data collection.
* **[Meter Phase](mdms_master/M_ServicePoint_MeterPhase.md)**
  * *Description:* Physical phase configurations of meters (1 PH, 3 PH, HT).
* **[Network Hierarchy](mdms_master/M_Network_Hierarchy.md)**
  * *Description:* Tiers of the physical grid (Substation, Feeder, DTR).
* **[Organisation Hierarchy](mdms_master/M_Organisation_Hierarchy.md)**
  * *Description:* Structural levels of the utility (HQ, Circle, Division, Subdivision, Section).

## Relationship Map
* **[Relationships](mdms_master/relationships.md)** – Canonical join graph and alias recommendations for mdms_master.