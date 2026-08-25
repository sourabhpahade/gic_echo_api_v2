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

## Relationship Map – prepaid

### 1. Daily Consumption & Archive Joins
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

### 2. Payment Joins
The `prepaid.dbo.t_payment` (Alias: tp) table maps financial recharges back to the core operational entities.

* **Target:** `mdms_master.dbo.l_consumer_lookup` (Alias: lcl)
  * **Join Logic:** `tp.Consumer_TblRefid = lcl.Consumer_TblRefID`
  * **Purpose:** Links a recharge/payment to the consumer who made it.
* **Target:** `mdms_master.dbo.l_meter_lookup` (Alias: lml)
  * **Join Logic:** `tp.MeterLookup_TblRefID = lml.MeterLookup_TblRefID`
  * **Purpose:** Links the recharge to the specific smart meter.

### 3. Meter Command Details Joins
The `prepaid.dbo.s_meter_commanddetails` (Alias: smcd) table tracks the execution of Disconnection (DC) and Reconnection (RC) commands.

* **Target:** `mdms_master.dbo.l_meter_lookup` (Alias: lml)
  * **Join Logic:** `smcd.MeterLookup_TblRefID = lml.MeterLookup_TblRefID`
  * **Purpose:** Identifies which meter the command was issued against.
* **Target:** `mdms_master.dbo.m_hes` (Alias: mhes)
  * **Join Logic:** `smcd.HESID = mhes.HESID`
  * **Purpose:** Identifies which Head-End System was responsible for executing the command.

### 4. Important Implementation Rules
1. **Enum Optimization:** Do not join to `mdms_master.dbo.m_connection_category` or `mdms_master.dbo.m_hes` if you only need to filter by their ID values, as the IDs are already documented directly in the column Enums of the `prepaid` tables.

## Table: s_meter_commanddetails

### Description
This table stores the history and status of automated meter commands triggered by the prepaid module. Specifically, it tracks Disconnection (DC) commands when a consumer's wallet balance drops too low, and Reconnection (RC) commands when the balance is restored. It monitors the lifecycle of these commands including retries and final execution statuses from the Head-End System (HES).

### Columns
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

## Table: t_dailyconsumption

### Description
This table stores the daily prepaid account summaries for consumers. It tracks daily and monthly energy consumption, captures wallet balances (opening and available), and records all daily financial deductions including energy charges, fixed charges, meter rent, and installments.

### Columns
* **DPTblRefID** (bigint): Unique internal identity number for the prepaid account record.
* **EntryDateTime** (datetime): Timestamp when the prepaid account record for the current day was entered into the system.
* **Consumer_TblRefID** (bigint): FOREIGN KEY to `mdms_master.dbo.l_consumer_lookup`. Maps the prepaid account record to the consumer.
* **RRNumber** (varchar): Unique identifier (account number) associated with the consumer.
* **MeterLookup_TblRefID** (bigint): PRIMARY KEY (Composite). FOREIGN KEY to `mdms_master.dbo.l_meter_lookup`. 
* **ConsumptionDate** (date): PRIMARY KEY (Composite). The specific date this prepaid account/consumption record represents.
* **MSN** (varchar): PRIMARY KEY (Composite). Unique Meter Serial Number associated with the consumer.
* **SL** (float): Sanctioned load of the consumer.
* **ConnectionCategory_TblRefID** (int): FOREIGN KEY to `mdms_master.dbo.m_connection_category`. Maps to the consumer's tariff category.
* **installment** (float): Installment amount scheduled to be deducted.
* **DayNo** (int): The day number of the consumer's billing cycle (resets every month).
* **daykWh** (float): Consumer's energy consumption for the day in kWh.
* **daykVAh** (float): Consumer's energy consumption for the day in kVAh.
* **monthkWh** (float): Consumer's accumulated energy consumption for the month in kWh.
* **monthkVAh** (float): Consumer's accumulated energy consumption for the month in kVAh.
* **dayConsumption** (float): Billed consumption for the day (metric defined by the `Unit` column).
* **monthConsumption** (float): Accumulated billed consumption for the month.
* **MeterReading_TimeStamp** (datetime): Timestamp of the last received daily profile readings.
* **previousReadingkWh** (float): Last recorded kWh reading.
* **presentReadingkWh** (float): Current day's kWh reading.
* **previousReadingkVAh** (float): Last recorded kVAh reading.
* **presentReadingkVAh** (float): Current day's kVAh reading.
* **isProcessed** (smallint, Enum: `-1`='DP not received', `0`='DP received, consumptions updated', `1`='Calculation completed'): Processing status of the prepaid account for the day.
* **processedTimeStamp** (datetime): Timestamp when the `isProcessed` status was last updated.
* **dayEnergyCharge** (float): Energy charges deducted for the day.
* **dayFixedCharge** (float): Fixed charges deducted for the day.
* **dayMeterRent** (float): Meter rent deducted for the day.
* **dayInstallment** (float): Installment amount deducted for the day.
* **DayOpeningBalance** (float): Consumer's opening wallet balance for the day.
* **totalAvailableAmount** (float): Consumer's current available wallet balance.
* **dayCreditAdjust** (float): Amount credited to the consumer's wallet during the day.
* **dayDebitAdjust** (float): Amount debited from the consumer's wallet during the day.
* **billdaybalance** (float): Consumer's opening wallet balance on the 1st day of the billing month.
* **isdpmissing** (int, Enum: `0`='No', `1`='Yes'): Flag indicating if the daily profile (DP) is missing for the current day.
* **last_dp_date** (date): The date of the last successfully received daily profile (DP).
* **MonthEnergyCharge** (float): Accumulated energy charges deducted for the month.
* **MonthFixedCharge** (float): Accumulated fixed charges deducted for the month.
* **MonthMeterRent** (float): Accumulated meter rent deducted for the month.
* **MonthInstallment** (float): Accumulated installments deducted for the month.
* **SettlementDeductedAmount** (float): Total settlement amount deducted (negative value indicates credit, positive value indicates debit).
* **SettlementOutstandingAmount** (float): Total outstanding settlement amount (negative value indicates credit, positive value indicates debit).
* **virtual_cr** (float): Virtual credit received in a day.
* **virtual_dr** (float): Virtual debit received in a day.
* **Inv_CreditAmount** (float): Amount credited via invoice.
* **Inv_DebitAmount** (float): Amount debited via invoice.
* **ArrearOutstandingAmount** (float): Outstanding installment amount for the current month.
* **Total_ArrearOutstandingAmt** (float): Total overall outstanding installment amount.
* **dayED** (float): Electricity Duty (ED) charges deducted for the day.
* **dayGovtSubsidy** (float): Government subsidy credited/applied for the day.
* **dayRebate** (float): Rebate amount applied for the day.
* **monthED** (float): Accumulated Electricity Duty (ED) charges for the month.
* **monthGovtSubsidy** (float): Accumulated government subsidy for the month.
* **monthRebate** (float): Accumulated rebate amount for the month.
* **Unit** (varchar, Enum: `KWH`, `KVAH`): Specifies the unit of measurement used to calculate the prepaid charges.

## Table: t_dailyconsumption_arch

### Description
This is the archival history table for `t_dailyconsumption`. It stores historical daily prepaid account summaries for consumers for past days. It tracks past daily and monthly energy consumption, historical wallet balances, and records all previous daily financial deductions (energy charges, fixed charges, meter rent, and installments).

### Columns
* **DPTblRefID** (bigint): Unique internal identity number for the prepaid account record.
* **EntryDateTime** (datetime): Timestamp when the prepaid account record was entered into the system.
* **Consumer_TblRefID** (bigint): FOREIGN KEY to `mdms_master.l_consumer_lookup`. Maps the prepaid account record to the consumer.
* **RRNumber** (varchar): Unique identifier (account number) associated with the consumer.
* **MeterLookup_TblRefID** (bigint): PRIMARY KEY (Composite). FOREIGN KEY to `mdms_master.l_meter_lookup`. 
* **ConsumptionDate** (date): PRIMARY KEY (Composite). The specific historical date this prepaid account/consumption record represents.
* **MSN** (varchar): PRIMARY KEY (Composite). Unique Meter Serial Number associated with the consumer.
* **SL** (float): Sanctioned load of the consumer.
* **ConnectionCategory_TblRefID** (int): FOREIGN KEY to `mdms_master.m_connection_category`. Maps to the consumer's tariff category.
* **installment** (float): Installment amount scheduled to be deducted.
* **DayNo** (int): The day number of the consumer's billing cycle (resets every month).
* **daykWh** (float): Consumer's energy consumption for the day in kWh.
* **daykVAh** (float): Consumer's energy consumption for the day in kVAh.
* **monthkWh** (float): Consumer's accumulated energy consumption for the month in kWh.
* **monthkVAh** (float): Consumer's accumulated energy consumption for the month in kVAh.
* **dayConsumption** (float): Billed consumption for the day (metric defined by the `Unit` column).
* **monthConsumption** (float): Accumulated billed consumption for the month.
* **MeterReading_TimeStamp** (datetime): Timestamp of the last received daily profile readings.
* **previousReadingkWh** (float): Last recorded kWh reading.
* **presentReadingkWh** (float): Current day's kWh reading.
* **previousReadingkVAh** (float): Last recorded kVAh reading.
* **presentReadingkVAh** (float): Current day's kVAh reading.
* **isProcessed** (smallint, Enum: `-1`='DP not received', `0`='DP received, consumptions updated', `1`='Calculation completed'): Processing status of the prepaid account for the day.
* **processedTimeStamp** (datetime): Timestamp when the `isProcessed` status was last updated.
* **dayEnergyCharge** (float): Energy charges deducted for the day.
* **dayFixedCharge** (float): Fixed charges deducted for the day.
* **dayMeterRent** (float): Meter rent deducted for the day.
* **dayInstallment** (float): Installment amount deducted for the day.
* **DayOpeningBalance** (float): Consumer's opening wallet balance for the day.
* **totalAvailableAmount** (float): Consumer's current available wallet balance.
* **dayCreditAdjust** (float): Amount credited to the consumer's wallet during the day.
* **dayDebitAdjust** (float): Amount debited from the consumer's wallet during the day.
* **billdaybalance** (float): Consumer's opening wallet balance on the 1st day of the billing month.
* **isdpmissing** (int, Enum: `0`='No', `1`='Yes'): Flag indicating if the daily profile (DP) was missing for this historical day.
* **last_dp_date** (date): The date of the last successfully received daily profile (DP).
* **MonthEnergyCharge** (float): Accumulated energy charges deducted for the month.
* **MonthFixedCharge** (float): Accumulated fixed charges deducted for the month.
* **MonthMeterRent** (float): Accumulated meter rent deducted for the month.
* **MonthInstallment** (float): Accumulated installments deducted for the month.
* **SettlementDeductedAmount** (float): Total settlement amount deducted (negative value indicates credit, positive value indicates debit).
* **SettlementOutstandingAmount** (float): Total outstanding settlement amount (negative value indicates credit, positive value indicates debit).
* **virtual_cr** (float): Virtual credit received in a day.
* **virtual_dr** (float): Virtual debit received in a day.
* **Inv_CreditAmount** (float): Amount credited via invoice.
* **Inv_DebitAmount** (float): Amount debited via invoice.
* **ArrearOutstandingAmount** (float): Outstanding installment amount for the month.
* **Total_ArrearOutstandingAmt** (float): Total overall outstanding installment amount.
* **dayED** (float): Electricity Duty (ED) charges deducted for the day.
* **dayGovtSubsidy** (float): Government subsidy credited/applied for the day.
* **dayRebate** (float): Rebate amount applied for the day.
* **monthED** (float): Accumulated Electricity Duty (ED) charges for the month.
* **monthGovtSubsidy** (float): Accumulated government subsidy for the month.
* **monthRebate** (float): Accumulated rebate amount for the month.
* **Unit** (varchar, Enum: `KWH`, `KVAH`): Specifies the unit of measurement used to calculate the prepaid charges.

## Table: t_payment

### Description
This table records all financial inflow/recharge events for consumer prepaid wallets. It captures the transaction amounts, dates, and the specific source of the recharge (e.g., whether the consumer paid via the mobile app/portal or if the recharge was processed through the discom's internal billing system). 

### Columns
* **PMT_TblRefID** (bigint): Unique internal identity number for the payment record.
* **EntryDateTime** (datetime): Timestamp when the payment record was entered into the system.
* **Consumer_TblRefid** (bigint): FOREIGN KEY to `mdms_master.dbo.l_consumer_lookup`. Maps the payment to the consumer.
* **MeterLookup_TblRefID** (bigint): FOREIGN KEY to `mdms_master.dbo.l_meter_lookup`. Maps the payment to the specific smart meter.
* **RequestID** (varchar): Unique request identifier associated with the recharge request.
* **RRNumber** (varchar): Unique identifier (number) associated with the consumer.
* **InstallationNumber** (varchar): Installation number associated with the consumer/meter setup.
* **RechargeAmount** (numeric): The financial amount credited to the prepaid wallet during this transaction.
* **txnID** (varchar): PRIMARY KEY. Unique transaction ID for the recharge (this column also stores the discom transaction ID).
* **RechargeDate** (datetime): The date and time when the recharge was successfully processed.
* **AmountAtLastRecharge** (numeric): The wallet balance amount immediately prior to this recharge being applied.
* **txnSource_TblRefid** (int, Enum: `1`='discom/utility/rms/billing system', `2`='consumer app/portal'): Indicates the origin or source platform of the recharge transaction.
* **UtilityReceiptNumber** (varchar): Receipt number generated by the utility's internal billing system, if applicable.

