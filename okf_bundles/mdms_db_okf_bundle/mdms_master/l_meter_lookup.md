---
type: Table
title: l_meter_lookup
description: Core table storing physical and logical details of smart meters, their configuration, and mapping to consumers and networks.
database: mdms_master
default_alias: lml
tags: 
- meter
- smart meter
- hardware
- installation
---

# Table: l_meter_lookup

## Description
This table contains the hardware records for all smart meters in the system. It tracks the physical properties (manufacturer, phase, meter type), configuration (multiplying factor, net metering), and logical mappings to consumers, networks, and organizations.

## Columns
* **MeterLookup_TblRefID** (int): PRIMARY KEY. Unique internal identity number for each smart meter.
* **Consumer_TblRefID** (int): FOREIGN KEY to `l_consumer_lookup`. Maps the smart meter to its attached consumer.
* **Meter_Serial_Number** (varchar): Unique serial number of the smart meter.
* **HESID** (smallint): FOREIGN KEY to `m_hes`. Maps the meter to its corresponding Head-End System (HES).
* **ServicePointMeterPhase_TblRefID** (int): FOREIGN KEY to `m_servicepoint_meterphase`. Stores the phase configuration of the smart meter.
* **DeviceManufacturer_TblRefID** (int): FOREIGN KEY to `m_device_manufacturer`. Stores the manufacturer of the smart meter.
* **NetworkLookup_TblRefID** (int): FOREIGN KEY to `l_network_lookup`. Maps the smart meter to its parent network (generally the DTR Network).
* **OrganisationLookup_TblRefID** (int): FOREIGN KEY to `l_organisation_lookup`. Maps the smart meter to its specific organizational hierarchy.
* **MF** (float): Stores the multiplying factor (MF) of the smart meter.
* **IsActiveStatus** (bit, Enum: `0`='No', `1`='Yes'): Indicates if the meter is currently in an active state.
* **IsNetMeter** (bit, Enum: `0`='No', `1`='Yes'): Indicates whether the smart meter functions as a net meter.
* **netmeter_change_ts** (datetime): Date and time when the net meter function was enabled in the smart meter.
* **InstallationDate** (datetime): Date and time when the smart meter was physically installed.
* **MeterType_TblRefID** (int, Enum: `1`='feeder meter', `2`='DT meter', `3`='consumer meter'): FOREIGN KEY to `m_meter_type`. Defines the physical placement or type of the smart meter.