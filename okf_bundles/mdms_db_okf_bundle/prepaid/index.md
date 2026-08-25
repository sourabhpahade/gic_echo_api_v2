---
type: DatabaseIndex
title: Prepaid Database
description: Core operational database managing prepaid consumer wallets, daily billing calculations, payments, and automated meter commands.
database_alias: prepaid
---

# Prepaid Database Index

This database manages the financial and operational lifecycle of prepaid consumers. It tracks daily wallet balances, applies daily energy and fixed charge deductions, records consumer recharges, and automates remote disconnection/reconnection (DC/RC) commands based on available wallet funds.

## Navigation Guide for Agents
1. Start here or in the root bundle index.
2. Always consult `relationships.md` before writing multi-table SQL.


## Core Fact Tables

### Billing & Wallet Management
* **[Daily Consumption](prepaid/t_dailyconsumption.md)**
  * *Description:* Active daily fact table tracking current day's energy consumption, wallet balances (opening/available), and all financial deductions (energy charges, fixed charges, installments).
  * *Keywords:* daily profile, wallet balance, deductions, charges, consumption.
* **[Daily Consumption Archive](prepaid/t_dailyconsumption_arch.md)**
  * *Description:* Archival history table storing all past days' records of consumer consumption, wallet balances, and applied charges.
  * *Keywords:* archive, historical, past days, historical balance.

### Financial Transactions
* **[Payments](prepaid/t_payment.md)**
  * *Description:* Fact table recording all consumer prepaid recharges and payments, differentiating between utility billing system recharges and consumer app/portal recharges.
  * *Keywords:* payment, recharge, wallet inflow, transaction, discom.

### Automated Operations
* **[Meter Command Details](prepaid/s_meter_commanddetails.md)**
  * *Description:* Tracks the history and execution status of Remote Disconnection (DC) and Reconnection (RC) commands triggered automatically by prepaid wallet balance thresholds.
  * *Keywords:* command, disconnection, reconnection, dc, rc, pending, processed.

## Relationship Map
* **[Relationships](prepaid/relationships.md)** – Canonical join graph and alias recommendations for the prepaid database, including cross-database joins to `mdms_master`.