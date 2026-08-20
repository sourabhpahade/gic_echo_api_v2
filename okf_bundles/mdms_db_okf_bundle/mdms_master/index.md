---
type: DatabaseIndex
title: MDMS Master Database
description: Core operational database for MDMS consumer and meter data.
database_alias: mdms_master
---

# MDMS Master Database Index

This database handles the core operational data for smart meter installations, consumer details, and the master lookup tables that define system statuses and categories.

## Navigation Guide for Agents

1. Start here or in the root bundle index.
2. Always consult `relationships.md` before writing multi-table SQL.
3. Only join tables that appear in the documented joins.

## Core Operational Tables
These are the primary transaction and entity tables:

| Table File | Description | Keywords / Synonyms | 
| :--- | :--- | :--- | 
| [Consumer Table](mdms_master/l_consumer_lookup.md) | Core consumer details, statuses, and account configurations. | consumer, rrnumber, account, statuses |
| [Meter Lookup](mdms_master/l_meter_lookup.md) | Smart meter hardware details, physical properties, and installation data. | meter, smart meter, hardware, physical |

## Master Tables
These tables define the enums, categories, and configurations used by the core operational tables:

| Table File                                                        | Description                                                        | Keywords / Synonyms                               |     |
| :---------------------------------------------------------------- | :----------------------------------------------------------------- | :------------------------------------------------ | --- |
| [Connection Status](mdms_master/M_Connection_Status.md)        | Defines connected, disconnected, or permanent disconnected states. | connection status, active, disconnected, state    |     |
| [Connection Category](mdms_master/M_Connection_Category.md)    | Tariff and connection categorization.                              | tariff, commercial, residential, category         |     |
| [Bill Cycle](mdms_master/M_BillCycle.md)                       | Billing frequencies (monthly, quarterly, etc.).                    | bill cycle, monthly, quarterly, frequency         |     |
| [Payment Type Contract](mdms_master/M_PaymentType_Contract.md) | Payment modes like prepaid or postpaid.                            | payment contract, prepaid, postpaid, payment mode |     |
| [Sanctioned Load Type](mdms_master/M_SL_TYPE.md)               | Units of measurement for power (kW, kVA, HP).                      | load unit, kw, kva, hp, measurement               |     |
| [Connection Type](mdms_master/M_ConnectionType.md)             | Nature of the connection (normal, government, etc.).               | connection type, normal, government               |     |
| [Billing Source](mdms_master/M_BillingSource.md)               | The system or entity responsible for consumer billing.             | billing source, entity, responsible               |     |

## Relationship Map
- [relationships.md](relationships.md) – Canonical join graph and alias recommendations