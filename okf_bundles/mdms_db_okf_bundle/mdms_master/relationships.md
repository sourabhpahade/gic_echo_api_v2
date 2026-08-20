---
type: relationships
title: MDMS Master Database – Relationship Map
database: mdms_master
description: Canonical join graph and relationship rules for all tables currently documented in this OKF bundle.
---

# Relationship Map – mdms_master_db

## 1. Core Fact Table Joins
The central table is `l_consumer_lookup` (Alias: lcl).

* **Target Table:** `l_meter_lookup` (Alias: lml)
  * **Join Logic:** `lcl.MeterLookup_TblRefId = lml.MeterLookup_TblRefID`
  * **Purpose:** Links one consumer to one primary smart meter.

## 2. Master & Lookup Table Joins
The following tables have a Many-to-One relationship originating from `l_consumer_lookup`.

* **Target Table:** `M_Connection_Status` (Alias: mcs_status)
  * **Join Logic:** `lcl.ConnectionStatus_TblRefID = M_Connection_Status.ConnectionStatus_TblRefID`
  * **Purpose:** Gets the primary connection / relay status.

* **Target Table:** `M_Connection_Status` (Alias: mcs_account)
  * **Join Logic:** `lcl.accntstatus_tblrefid = M_Connection_Status.ConnectionStatus_TblRefID`
  * **Purpose:** Gets the secondary / account status (Requires joining this table a second time).

* **Target Table:** `M_Connection_Category` (Alias: mcc)
  * **Join Logic:** `lcl.ConnectionCategory_TblRefID = M_Connection_Category.ConnectionCategory_TblRefID`
  * **Purpose:** Gets the tariff / consumer category.

* **Target Table:** `M_BillCycle` (Alias: mbc)
  * **Join Logic:** `lcl.BillcycleTblRefiID = M_BillCycle.billcycleTblRefiID`
  * **Purpose:** Gets the billing frequency.

* **Target Table:** `M_PaymentType_Contract` (Alias: mptc)
  * **Join Logic:** `lcl.PaymentContract_TblRefID = M_PaymentType_Contract.PaymentContract_TblRefID`
  * **Purpose:** Identifies if the consumer is on a Prepaid or Postpaid contract.

* **Target Table:** `M_SL_TYPE` (Alias: msl)
  * **Join Logic:** `lcl.SL_TYPE_ID = M_SL_TYPE.SL_TYPE_ID`
  * **Purpose:** Gets the unit of sanctioned load.

* **Target Table:** `M_ConnectionType` (Alias: mct)
  * **Join Logic:** `lcl.ConnectionTypeTblRefID = M_ConnectionType.ConnectionTypeTblRefID`
  * **Purpose:** Gets the nature of the connection.

* **Target Table:** `M_BillingSource` (Alias: mbs)
  * **Join Logic:** `lcl.BillingSource_TblRefID = M_BillingSource.BillingSource_TblRefID`
  * **Purpose:** Gets the source system of the billing data.

## 3. Important Implementation Notes
1. **Double Joins:** `M_Connection_Status` is intentionally joined twice with different aliases when both connection and account statuses are required.
2. **Exact Spelling:** Column name spelling must be respected exactly as written (e.g., `BillcycleTblRefiID` vs `billcycleTblRefiID`).