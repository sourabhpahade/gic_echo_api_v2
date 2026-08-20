---
type: Table
title: l_meter_lookup
description: [Add general description of this table's purpose, e.g., Master table storing smart meter hardware details, installation data, and physical properties.]
database: mdms_master
default_alias: lml
tags: 
- meter
- hardware
- smart meter
---

# Table: l_meter_lookup

## Description
[Add general description of this table's purpose, e.g., Master table storing smart meter hardware details, installation data, and physical properties.]

[Add business context here: When is a record created? What does one row represent? e.g., One row represents a single physical smart meter device deployed in the field.]

## Columns
* **MeterLookup_TblRefID** (int): [Add description]
* **Consumer_TblRefID** (int): [Add description]
* **Meter_Serial_Number** (varchar): [Add description]
* **HESID** (smallint): [Add description]
* **ServicePointMeterPhase_TblRefID** (int): [Add description]
* **DeviceManufacturer_TblRefID** (int): [Add description]
* **NetworkLookup_TblRefID** (int): [Add description]
* **OrganisationLookup_TblRefID** (int): [Add description]
* **MF** (float): [Add description]
* **lsfrequency** (tinyint): [Add description]
* **TimeOfDay_TblRefID** (int): [Add description]
* **IsActiveStatus** (bit, Enum: `0`='False', `1`='True'): [Add description]
* **IsTestMeter** (bit, Enum: `0`='False', `1`='True'): [Add description]
* **IsNetMeter** (bit, Enum: `0`='False', `1`='True'): [Add description]
* **InstallationDate** (datetime): [Add description]
* **InitialReading** (float): [Add description]
* **Sealno_1** (varchar): [Add description]
* **Sealno_2** (varchar): [Add description]
* **Sealno_3** (varchar): [Add description]
* **Sealno_4** (varchar): [Add description]
* **Sealno_5** (varchar): [Add description]
* **Sealno_6** (varchar): [Add description]
* **Sealno_7** (varchar): [Add description]
* **Sealno_8** (varchar): [Add description]
* **Latitude** (float): [Add description]
* **Longitude** (float): [Add description]
* **IsDCU** (bit, Enum: `0`='False', `1`='True'): [Add description]
* **DCUID** (smallint): [Add description]
* **CommunicationID** (smallint): [Add description]
* **NonOperationID** (smallint): [Add description]
* **MECT** (varchar): [Add description]
* **MEPT** (varchar): [Add description]
* **MeterCT** (float): [Add description]
* **MeterPT** (float): [Add description]
* **Dial_Factor** (float): [Add description]
* **EntryLoginCode** (int): [Add description]
* **EntryUserCode** (int): [Add description]
* **EntryDateTime** (datetime): [Add description]
* **UpdateLoginCode** (int): [Add description]
* **UpdateUserCode** (int): [Add description]
* **UpdateDateTime** (datetime): [Add description]
* **Remarks** (varchar): [Add description]
* **MSNMAKE** (varchar): [Add description]
* **SUPPLY_VTG_TblRefID** (int): [Add description]
* **IsCheckMeter** (bit, Enum: `0`='False', `1`='True'): [Add description]
* **CheckMeterNo** (tinyint): [Add description]
* **Consumer_Tag** (varchar): [Add description]
* **Consumer_Group** (varchar): [Add description]
* **Meter_Rating** (varchar): [Add description]
* **MeterType_TblRefID** (int): [Add description]
* **netmeter_change_ts** (datetime): [Add description]
* **sat_tblrefid** (int): [Add description]
* **InstallationBy** (int): [Add description]
* **Installation_Source** (varchar): [Add description]
* **con_sup_tblrefid** (int): [Add description]
* **ismodemavail** (int): [Add description]