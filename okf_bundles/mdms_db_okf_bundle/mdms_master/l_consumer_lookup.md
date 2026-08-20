---
type: Table
title: l_consumer_lookup
description: This table contains information about consumers present in meter data management system (mdms), including details consumer name, address, connection type, connection status along with various other attributes.
database: mdms_master
default_alias: lcl
tags: 
- consumer
- rrnumber
- consumer details
---

# Table: l_consumer_lookup

## Description
This table contains information about consumers present in the meter data management system (mdms), including consumer name, address, connection type, connection status, and various other attributes.  
In this table, the entry of records happens after smart meter installation is completed in a consumer's premise.  

## Columns
* **Consumer_TblRefID** (int): Unique, incremental identity column used as the primary reference for this table.
* **MeterLookup_TblRefId** (bigint): Defines the relationship between the consumer and the smart meter attached to them.
* **RRNumber** (varchar): Unique Identifier number for each consumer.
* **Consumer_Name** (nvarchar): Name of the consumer.
* **Consumer_FatherName** (nvarchar): Name of consumer's father.
* **ConnectionStatus_TblRefID** (smallint): Reference to connection status master table (connected, disconnected, or permanently disconnected).
* **ConnectionCategory_TblRefID** (int): Reference to consumer category master table (tariff category).
* **Consumer_Address** (nvarchar): Consumer's address.
* **Consumer_Pincode** (varchar): Consumer's pincode.
* **Consumer_MobileNumber** (varchar): Consumer's mobile number.
* **Consumer_LandLineNumber** (varchar): Consumer's land line number.
* **Consumer_Email** (varchar): Consumer's Email address.
* **Account_ID** (varchar): Unique installation number assigned for the smart meter installation request.
* **Sanctioned_Load_KW** (decimal): Maximum electrical power (kW/kVA) approved for the consumer.
* **Bill_Day** (smallint): The day of the month (1-31) the consumer's bill is generated.
* **BillcycleTblRefiID** (int): Reference to billing cycle master table (e.g., monthly, quarterly, yearly).
* **PaymentContract_TblRefID** (int): Reference to payment contract master table (e.g., prepaid, postpaid).
* **Nearest_AccountID** (varchar): Stores the rrnumber for old-to-smart meter installations, or NSC + account_id for new requests.
* **SL_TYPE_ID** (smallint): Reference to sl type master table (unit of sanctioned load: kw, kva, watt, HP).
* **Contract_Demand** (decimal): Specific amount of electrical power mutually agreed to be purchased by commercial/industrial consumers.
* **ServicePointMeterType_TblRefID** (smallint): Reference to service point meter type table (e.g., 1 phase, 3 phase).
* **ConnectionTypeTblRefID** (int): Reference to connection type master table (e.g., normal, government).
* **isPrevilege** (tinyint, Enum: `0`='No', `1`='Yes'): Defines whether consumer is privilege. Disconnection is not allowed for a given time period.
* **isStagger** (tinyint, Enum: `0`='No', `1`='Yes'): Defines whether consumer is staggered. Disconnection is not allowed for a given time period.
* **Installment** (float): Installment amount deducting daily from InstallmentStartDate to InstallmentEndDate.
* **InstallmentEndDate** (date): End date when deduction of installment amount stops.
* **isForceDisconnect** (tinyint, Enum: `0`='No', `1`='Yes'): If Yes, consumer meter will not be connected even with a positive wallet balance.
* **ForceDisconnectDateTime** (datetime): Date time when consumer was marked as force disconnected.
* **EntryTimeStamp** (datetime): Date time when consumer was created in MDMS.
* **Privilege_StartDate** (date): Start date for privilege functionality.
* **Privilege_Enddate** (date): End date for privilege functionality.
* **isTOD** (tinyint, Enum: `0`='No', `1`='Yes'): Defines whether TOD (Time of day) billing is enabled.
* **MRU** (varchar): It defines in which MRU (Meter reading unit) a consumer belongs.
* **MasterSyncDate** (datetime): Date when utility/discom shared the acknowledgment of installment data response.
* **RC_DC_DateTime** (datetime): Date time of the last reconnection or disconnection.
* **Stagger_Start_date** (datetime): Start date for stagger functionality.
* **Stagger_End_date** (datetime): End date for stagger functionality.
* **ServiceDate** (datetime): Date time when smart meter was installed in consumer's premise.
* **isLRCF** (bit, Enum: `null`='not used', `0`='used by consumer', `1`='LRCF was reset'): State of Local Relay Connect Functionality.
* **LRCF_UpdateDateTime** (datetime): Date time of latest action taken on LRCF (enabled or reset via command).
* **InstallmentStartDate** (date): Start date of installment amount deduction.
* **Installment_Received_DateTime** (datetime): Date time when the latest installment details were received.
* **Discom_Push_Date** (datetime): It is a date time when the meter replacement response was pushed to utility.