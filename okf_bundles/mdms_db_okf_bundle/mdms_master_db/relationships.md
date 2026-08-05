---
type: relationships
title: MDMS Master Database – Relationship Map
database: mdms_master
description: Canonical join graph and relationship rules for all tables currently documented in this OKF bundle.
tags: [relationships, joins, erd, graph]
---

# Relationship Map – mdms_master_db

## 1. Core Fact Tables (1 : 1 / 1 : 0..1)

```
l_consumer_lookup (lcl)
        │
        │  lcl.MeterLookup_TblRefId = lml.MeterLookup_TblRefID
        ▼
l_meter_lookup (lml)
```

- One consumer is linked to one primary smart meter.
- The foreign key lives on the **consumer** side.

## 2. Consumer → Lookup / Master Tables

All of the following are many-to-one relationships from `l_consumer_lookup`.

| Consumer Column                    | Master Table              | Master PK                     | Recommended Alias | Notes                                      |
|------------------------------------|---------------------------|-------------------------------|-------------------|--------------------------------------------|
| ConnectionStatus_TblRefID          | M_Connection_Status       | ConnectionStatus_TblRefID     | mcs_status        | Primary connection / relay status          |
| accntstatus_tblrefid               | M_Connection_Status       | ConnectionStatus_TblRefID     | mcs_account       | Secondary / account status (same table)    |
| ConnectionCategory_TblRefID        | M_Connection_Category     | ConnectionCategory_TblRefID   | mcc               | Tariff / consumer category                 |
| BillcycleTblRefiID                 | M_BillCycle               | billcycleTblRefiID            | mbc               | Billing frequency (note spelling)          |
| PaymentContract_TblRefID           | M_PaymentType_Contract    | PaymentContract_TblRefID      | mptc              | Prepaid / Postpaid                         |
| SL_TYPE_ID                         | M_SL_TYPE                 | SL_TYPE_ID                    | msl               | Unit of sanctioned load                    |
| ConnectionTypeTblRefID             | M_ConnectionType          | ConnectionTypeTblRefID        | mct               | Nature of connection                       |
| BillingSource_TblRefID             | M_BillingSource           | BillingSource_TblRefID        | mbs               | Source system of billing data              |

## 3. Visual Summary (text ERD)

```
                    ┌──────────────────────┐
                    │  M_Connection_Status │
                    │  (mcs_status /       │
                    │   mcs_account)       │
                    └──────────┬───────────┘
                               │
┌──────────────────────┐       │       ┌─────────────────────────┐
│  M_Connection_Category│◄──────┼──────►│  M_PaymentType_Contract │
│  (mcc)                │       │       │  (mptc)                 │
└──────────────────────┘       │       └─────────────────────────┘
                               │
┌──────────────────────┐       │       ┌─────────────────────────┐
│  M_BillCycle (mbc)   │◄──────┼──────►│  M_SL_TYPE (msl)        │
└──────────────────────┘       │       └─────────────────────────┘
                               │
┌──────────────────────┐       │       ┌─────────────────────────┐
│  M_ConnectionType    │◄──────┼──────►│  M_BillingSource (mbs)  │
│  (mct)               │       │       └─────────────────────────┘
└──────────────────────┘       │
                               │
                    ┌──────────▼───────────┐
                    │  l_consumer_lookup   │
                    │  (lcl)               │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  l_meter_lookup      │
                    │  (lml)               │
                    └──────────────────────┘
```

## 4. Important Implementation Notes for the Agent

1. **Always prefer the aliases defined in this file and in the individual table documents.**
2. `M_Connection_Status` is intentionally joined **twice** with different aliases when both statuses are required.
3. Column name spelling must be respected exactly as written (`BillcycleTblRefiID`, `billcycleTblRefiID`, `MeterLookup_TblRefId` vs `MeterLookup_TblRefID`). MSSQL is usually case-insensitive, but the knowledge base must stay faithful to the real schema.
4. Many additional FKs exist on `l_meter_lookup` (DeviceManufacturer, Network, Organisation, MeterType, TimeOfDay, etc.). They are **not yet documented** in this bundle – do not invent joins for them.
5. When generating SQL, start from `l_consumer_lookup` (or `l_meter_lookup`) and only bring in masters that are actually needed for the user’s question.
