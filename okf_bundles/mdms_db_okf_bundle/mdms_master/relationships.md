---
type: relationships
title: MDMS Master Database – Relationship Map
database: mdms_master
description: Canonical join graph and relationship rules for all tables documented in the mdms_master OKF bundle.
---

# Relationship Map – mdms_master

## 1. Consumer Core Joins
The central entity is `l_consumer_lookup` (Alias: lcl).

* **Target:** `l_meter_lookup` (Alias: lml)
  * **Join Logic:** `lcl.MeterLookup_TblRefId = lml.MeterLookup_TblRefID`
  * **Purpose:** Links one consumer to their primary installed smart meter.
* **Target:** `m_connection_status` (Alias: mcs)
  * **Join Logic:** `lcl.ConnectionStatus_TblRefID = mcs.ConnectionStatus_TblRefID`
  * **Purpose:** Gets the physical connectivity/relay status.
* **Target:** `m_connection_category` (Alias: mcc)
  * **Join Logic:** `lcl.ConnectionCategory_TblRefID = mcc.ConnectionCategory_TblRefID`
  * **Purpose:** Gets the consumer's tariff/category (e.g., Domestic, Commercial).
* **Target:** `m_paymenttype_contract` (Alias: mptc)
  * **Join Logic:** `lcl.PaymentContract_TblRefID = mptc.PaymentContract_TblRefID`
  * **Purpose:** Identifies if the consumer is Prepaid or Postpaid.
* **Target:** `m_sl_type` (Alias: mslt)
  * **Join Logic:** `lcl.SL_TYPE_ID = mslt.SL_TYPE_ID`
  * **Purpose:** Gets the unit of measurement for sanctioned load.

## 2. Meter Hardware & Mapping Joins
These joins originate from `l_meter_lookup` (Alias: lml) to define hardware specs and physical locations.

* **Target:** `m_hes` (Alias: mhes)
  * **Join Logic:** `lml.HESID = mhes.HESID`
  * **Purpose:** Maps the meter to its communicating Head-End System.
* **Target:** `m_servicepoint_meterphase` (Alias: msmp)
  * **Join Logic:** `lml.ServicePointMeterPhase_TblRefID = msmp.ServicePointMeterPhase_TblRefID`
  * **Purpose:** Gets the physical phase (1 Phase, 3 Phase, etc.).
* **Target:** `m_device_manufacturer` (Alias: mdm)
  * **Join Logic:** `lml.DeviceManufacturer_TblRefID = mdm.DeviceManufacturer_TblRefID`
  * **Purpose:** Identifies the smart meter's brand/manufacturer.
* **Target:** `l_network_lookup` (Alias: lnl)
  * **Join Logic:** `lml.NetworkLookup_TblRefID = lnl.NetworkLookup_TblRefID`
  * **Purpose:** Maps the smart meter to its parent network (usually a DTR).
* **Target:** `l_organisation_lookup` (Alias: l_org)
  * **Join Logic:** `lml.OrganisationLookup_TblRefID = l_org.OrganisationLookup_TblRefID`
  * **Purpose:** Maps the smart meter to its managing utility office.

## 3. Hierarchy & Self-Joins (Network & Organisation)
These tables map the grid and utility structure, using self-joins for parent-child navigation.

* **Network to Organisation:**
  * **Join Logic:** `l_network_lookup.OrganisationLookup_TblRefID = l_organisation_lookup.OrganisationLookup_TblRefID`
* **Network Master Lookups:**
  * **Join Logic:** `l_network_lookup.NetworkHierarchy_TblRefID = m_network_hierarchy.NetworkHierarchy_TblRefID`
* **Network Self-Join (Parent/Child):**
  * **Join Logic:** `child_net.HigherNetwork_ID = parent_net.NetworkLookup_TblRefID`
  * **Purpose:** E.g., Finding the Feeder for a specific DTR.
* **Organisation Master Lookups:**
  * **Join Logic:** `l_organisation_lookup.OrganisationHierarchy_TblRefID = m_organisation_hierarchy.OrganisationHierarchy_TblRefID`
* **Organisation Self-Join (Parent/Child):**
  * **Join Logic:** `child_org.HigherOffice_ID = parent_org.OrganisationLookup_TblRefID`
  * **Purpose:** E.g., Finding the Division for a specific Subdivision.

## 4. Important Implementation Rules
1. **Self-Referencing Aliases:** When writing SQL that traverses hierarchies, you MUST use distinct aliases for the parent and child tables (e.g., `l_organisation_lookup child_org` JOIN `l_organisation_lookup parent_org`).
2. **Enum Optimization:** Because master lookups like `m_connection_status`, `m_paymenttype_contract`, and `m_hes` have their ID values documented directly as `Enum` lists in the core table OKFs, **do not execute JOINs to these master tables just for basic `WHERE` filtering.** Only JOIN them if you need to `SELECT` the string name in the output.

## 5. Hierarchy Traversal Guide
When writing queries that require navigating up or down the organizational or network trees, strictly follow these structural chains. The `OrganisationHierarchy_TblRefID` and `NetworkHierarchy_TblRefID` determine the exact level.

### A. Organisation Chain (Top to Bottom)
1. **HQ** (`OrganisationHierarchy_TblRefID = 1`) -> *Highest Parent*
2. **Circle** (`OrganisationHierarchy_TblRefID = 2`)
3. **Division** (`OrganisationHierarchy_TblRefID = 3`)
4. **Subdivision** (`OrganisationHierarchy_TblRefID = 4`)
5. **Section** (`OrganisationHierarchy_TblRefID = 5`) -> *Lowest Child*

### B. Network Chain (Top to Bottom)

1. **Sub Station** (`NetworkHierarchy_TblRefID = 1`) -> _Highest Parent_
2. **Feeder** (`NetworkHierarchy_TblRefID = 2`)
3. **DTR** (`NetworkHierarchy_TblRefID = 3`) -> _Lowest Child_
_Note: Smart Meters are generally mapped to the DTR level via `l_meter_lookup.NetworkLookup_TblRefID`.

*Example of traversing up from Section to Division:*
```sql
SELECT section.Office_Name, division.Office_Name 
FROM l_organisation_lookup section
-- Join up to Subdivision
JOIN l_organisation_lookup subdiv ON section.HigherOffice_ID = subdiv.OrganisationLookup_TblRefID
-- Join up to Division
JOIN l_organisation_lookup division ON subdiv.HigherOffice_ID = division.OrganisationLookup_TblRefID
WHERE section.OrganisationHierarchy_TblRefID = 5;
