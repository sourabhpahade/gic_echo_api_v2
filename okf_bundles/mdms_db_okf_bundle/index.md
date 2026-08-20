---
type: GlobalIndex
title: Enterprise Database Directory
description: Stores the core databases within the mdms system for query routing.
---

# Enterprise Database Directory

This directory maps the core databases within the enterprise. Use this index to route natural language queries to the appropriate sub-domain indexes.

## Master Data
| Database Folder                             | Primary Purpose                                                                                                                | Keywords & Synonyms                                                      | Cross-Database Joins                                                      |
| :------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------- | :------------------------------------------------------------------------ |
| [mdms_master](./mdms_master/index.md) | Stores master data of Consumers, Smart Meter, DTR, Feeder, Organization Master i.e Division, Section, Subdivision, Circle etc. | consumer, customer, account, smart meter, hardware, disconnected, status | *(Add any related DBs here, e.g., `[/billing_db](/billing_db/index.md)`)* |