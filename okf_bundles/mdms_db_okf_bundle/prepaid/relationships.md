---
type: relationships
title: Prepaid Database – Relationship Map
database: prepaid
description: Canonical join graph and cross-database relationship rules for all tables in the prepaid OKF bundle, strictly using .dbo schema conventions.
---

# Relationship Map – prepaid

## 1. Daily Consumption & Archive Joins
Both `prepaid.dbo.t_dailyconsumption` (Alias: tdc) and `prepaid.dbo.t_dailyconsumption_arch` (Alias: tdca) share mappings to the master database, and can also be joined to each other for historical comparisons.

* **Target:** `prepaid.dbo.t_dailyconsumption_arch` (Alias: tdca)
  * **Source:** `prepaid.dbo.t_dailyconsumption` (Alias: tdc)
  * **Join Logic:** `tdc.Consumer_TblRefID = tdca.Consumer_TblRefID`
  * **Purpose:** Links the current day's billing and wallet record with a consumer's historical records to analyze trends or compare past balances/consumption.

* **Target:** `mdms_master.dbo.l_consumer_lookup` (Alias: lcl)
  * **Join Logic:** `tdc.Consumer_TblRefID = lcl.Consumer_TblRefID` (Applies to both `tdc` and `tdca`)
  * **Purpose:** Links the daily billing and wallet record to the core consumer profile.
* **Target:** `mdms_master.dbo.l_meter_lookup` (Alias: lml)
  * **Join Logic:** `tdc.MeterLookup_TblRefID = lml.MeterLookup_TblRefID` (Applies to both `tdc` and `tdca`)
  * **Purpose:** Links the daily record to the physical smart meter hardware.
* **Target:** `mdms_master.dbo.m_connection_category` (Alias: mcc)
  * **Join Logic:** `tdc.ConnectionCategory_TblRefID = mcc.ConnectionCategory_TblRefID` (Applies to both `tdc` and `tdca`)
  * **Purpose:** Identifies the tariff category under which the daily charges were calculated.

## 2. Payment Joins
The `prepaid.dbo.t_payment` (Alias: tp) table maps financial recharges back to the core operational entities.

* **Target:** `mdms_master.dbo.l_consumer_lookup` (Alias: lcl)
  * **Join Logic:** `tp.Consumer_TblRefid = lcl.Consumer_TblRefID`
  * **Purpose:** Links a recharge/payment to the consumer who made it.
* **Target:** `mdms_master.dbo.l_meter_lookup` (Alias: lml)
  * **Join Logic:** `tp.MeterLookup_TblRefID = lml.MeterLookup_TblRefID`
  * **Purpose:** Links the recharge to the specific smart meter.

## 3. Meter Command Details Joins
The `prepaid.dbo.s_meter_commanddetails` (Alias: smcd) table tracks the execution of Disconnection (DC) and Reconnection (RC) commands.

* **Target:** `mdms_master.dbo.l_meter_lookup` (Alias: lml)
  * **Join Logic:** `smcd.MeterLookup_TblRefID = lml.MeterLookup_TblRefID`
  * **Purpose:** Identifies which meter the command was issued against.
* **Target:** `mdms_master.dbo.m_hes` (Alias: mhes)
  * **Join Logic:** `smcd.HESID = mhes.HESID`
  * **Purpose:** Identifies which Head-End System was responsible for executing the command.

## 4. Important Implementation Rules
1. **Enum Optimization:** Do not join to `mdms_master.dbo.m_connection_category` or `mdms_master.dbo.m_hes` if you only need to filter by their ID values, as the IDs are already documented directly in the column Enums of the `prepaid` tables.