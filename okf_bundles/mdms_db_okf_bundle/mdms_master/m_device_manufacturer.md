---
type: Table
title: m_device_manufacturer
description: Master lookup table defining all smart meter and hardware manufacturers.
database: mdms_master
default_alias: mdm
tags: 
- manufacturer
- device manufacturer
- smart meter brand
- make
---

# Table: m_device_manufacturer

## Description
This master lookup table stores the complete list of authorized manufacturers and brands for smart meters and related hardware devices in the system. 

## Columns
* **DeviceManufacturer_TblRefID** (int, Enum: `1`='UTILITY', `2`='ACS', `3`='ADME', `4`='AEW', `5`='AI', `8`='AMTL', `9`='ANSHU', `10`='ANZU', `11`='ARON', `12`='ASSLTO', `13`='AT', `14`='AVON', `15`='AYONPCFR', `16`='BAJAJ', `17`='BEM', `18`='B-E-M', `19`='BENTEC', `20`='BENTEK', `21`='BENTEX', `22`='BHEL', `23`='BHM', `24`='BM', `25`='BPL', `26`='C and H', `27`='CLASS', `28`='DASS', `29`='DCD', `30`='DH', `31`='DLMS', `32`='DTRMETER', `33`='DUKE', `34`='DUMMY', `35`='EAW', `36`='EC', `37`='ECE', `38`='ELYMER', `39`='EMCO', `40`='EMLT', `41`='FERRANTI', `42`='FL', `43`='FLAP', `44`='FLASH', `45`='FLESH', `46`='FNUS', `47`='GE', `48`='GENUS', `49`='GM', `50`='GPI', `51`='GTIS', `52`='HAITEK', `53`='HARIYANA', `54`='HARYANA', `55`='HAVELLS', `56`='HEV', `57`='HI', `58`='HM', `59`='HPL', `60`='HSM', `61`='HT', `62`='HYTECH', `63`='IB', `64`='IGM', `65`='IM', `66`='INDIA', `67`='INDO FRANC', `68`='INDOTECH', `69`='IT', `70`='JAIPUR', `71`='JS,Baroda', `72`='L and G', `73`='LANDIS', `77`='LASEN', `78`='LENKAR', `81`='LINKWELL', `83`='LPT', `85`='LW', `86`='M and I', `87`='MADRAS', `88`='MANGAL', `89`='MBM', `90`='MGI', `91`='MI', `92`='MIG', `93`='MONTAIL', `94`='MONTEL', `95`='MONTEX', `96`='MOTRAL', `97`='MPVY', `98`='NACODA', `99`='NAK', `100`='NAKODA', `101`='NAMTECH', `102`='NEL', `103`='NKD', `104`='NM', `105`='PAL', `106`='PALMOAN', `107`='PALMOHA', `108`='PALMOHAN', `109`='PM', `110`='QTY', `111`='RC', `112`='REKKON', `113`='REMCO', `114`='RIKKEN', `115`='S', `116`='SCHLUMBERG', `120`='SECURE', `121`='SEMI COND', `123`='SIMCO', `124`='SINTEX', `125`='SOCOMEC', `126`='SOMAC', `128`='TGL', `129`='TLG', `130`='TOBRA', `131`='TRINCRGN', `132`='TTL', `133`='TURBO', `134`='UE', `135`='UNILAC', `136`='UNILEC', `137`='UNILIC', `138`='UNITED', `139`='UNIVERSAL', `140`='UNMETERED', `141`='UTAKE', `142`='VINOTEK', `143`='VISION', `144`='VISIONTAK', `145`='VISIONTAKE', `146`='VISIONTEC', `147`='VISIONTEK', `148`='VISIONTEX', `149`='VISNTEC', `150`='VISONTEK', `151`='VISTEC', `152`='VISTON', `153`='VS', `154`='VT', `155`='VTEK', `156`='VXL', `157`='VZS', `158`='WAATHOUR', `159`='WINNER', `160`='WPANLRAF', `162`='SARAL', `163`='GENRETION', `166`='L&T', `167`='Ametek', `168`='EL SEWEDY', `169`='GENTEK', `170`='INDIA PVT LTD', `171`='MAXWELL INDIA', `172`='PAL MOHAN', `173`='PLUTUS', `174`='POWER TECH', `175`='RMC INDIA', `176`='SEMI CONDUCTOR', `177`='SUNSTAR', `178`='VISION TECH', `179`='SCHNEIDER', `180`='OMNI AGATE', `181`='ISKRAEMECO', `261`='SWITCH GEAR', `262`='SEIPL', `263`='Capital', `301`='Kimbal', `302`='Sona Electricals Bhopal', `303`='Vishal Transformer and Switch gears'): PRIMARY KEY. Unique identifier for the device manufacturer.
* **Manufacturer_Name** (nvarchar): The full descriptive name of the device manufacturer.
* **isActive** (bit, Enum: `0`='No', `1`='Yes'): Indicates if the manufacturer is currently active and approved for use.