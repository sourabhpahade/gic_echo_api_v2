---
type: Table
title: t_dailyconsumption
description: Core daily fact table for prepaid consumers, tracking daily energy consumption, wallet balances, and deducted charges.
database: prepaid
default_alias: tdc
tags: 
- prepaid
- daily consumption
- wallet balance
- charges
- deductions
- daily profile
---

# Table: t_dailyconsumption

## Description
This table stores the daily prepaid account summaries for consumers. It tracks daily and monthly energy consumption, captures wallet balances (opening and available), and records all daily financial deductions including energy charges, fixed charges, meter rent, and installments.

## Columns
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