---
type: Table
title: s_meter_commanddetails
description: Tracks Remote Reconnection (RC) and Disconnection (DC) commands initiated by the prepaid module based on consumer wallet balances.
database: prepaid
default_alias: smcd
tags: 
- command
- disconnection
- reconnection
- dc
- rc
- prepaid
---

# Table: s_meter_commanddetails

## Description
This table stores the history and status of automated meter commands triggered by the prepaid module. Specifically, it tracks Disconnection (DC) commands when a consumer's wallet balance drops too low, and Reconnection (RC) commands when the balance is restored. It monitors the lifecycle of these commands including retries and final execution statuses from the Head-End System (HES).

## Columns
* **TblRefID** (bigint): Unique internal identity number for each command record.
* **CommandRequest_TblRefID** (varchar): Unique command request identifier used for tracking. If `NULL`, the command is logged but has not yet been triggered/sent to the meter.
* **MeterLookup_TblRefID** (bigint): PRIMARY KEY (Composite). FOREIGN KEY to `mdms_master.dbo.l_meter_lookup` (and by extension `mdms_master.dbo.l_consumer_lookup`).
* **MSN** (varchar): Unique Meter Serial Number associated with the consumer.
* **Command_TblRefID** (int, Enum: `32`='DC (Disconnection)', `33`='RC (Reconnection)'): PRIMARY KEY (Composite). Identifier dictating the type of command being executed.
* **EntryDateTime** (datetime): Timestamp when the command record was generated.
* **IsProcessed** (smallint, Enum: `0`='Pending', `1`='Processed'): Indicates whether the command has been processed by the system.
* **Processed_TimeStamp** (datetime): Timestamp when the command's processing was completed.
* **ProcessStatus** (varchar, Enum: `success`, `mansuccess`, `relsuccess`, `fail`): The final outcome of the command execution (only applicable when `IsProcessed` = 1).
* **RetryCount** (int): The total number of times the system has retried executing the command.
* **LastRetryDateTime** (datetime): Timestamp of the most recent retry attempt.
* **Command_date** (date): PRIMARY KEY (Composite). The date when the command was initially triggered.
* **HESID** (int): FOREIGN KEY to `mdms_master.dbo.m_hes`. Maps the command to the specific Head-End System responsible for the meter.
* **AvailableBalance** (float): The consumer's available prepaid wallet balance at the exact time the command was triggered.