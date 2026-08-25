---
type: GlobalIndex
title: Enterprise Database Directory
description: Stores the core databases within the mdms system for query routing.
---

# Enterprise Database Directory

This directory maps the core databases within the enterprise. Use this index to route natural language queries to the appropriate sub-domain indexes.

## 1. Master Data Database
* **Database Folder:** `./mdms_master/index.md`
* **Primary Purpose:** Stores static and structural master data. This includes details for Consumers, Smart Meters, DTRs, Feeders, and Organization Masters (Division, Section, Subdivision, Circle).
* **Keywords & Synonyms:** consumer, customer, account, smart meter, hardware, status, installation, geography, organization.

## 2. Prepaid Database
* **Database Folder:** `./prepaid/index.md`
* **Primary Purpose:** The core financial and operational engine for consumers on prepaid contracts. This database manages active and historical daily energy consumption (kWh/kVAh) alongside dynamic wallet balances, processing daily deductions for energy, fixed charges, installments, and subsidies. It serves as the central ledger for all recharge transactions (from consumer apps or utility portals) and automates physical grid operations by triggering and tracking Remote Disconnection (DC) and Reconnection (RC) meter commands based on wallet thresholds.
* **Keywords & Synonyms:** prepaid, balance, recharge, deduction, tariff, wallet, payment, financial, billing, reconnection (rc) and disconnection (dc) commands .