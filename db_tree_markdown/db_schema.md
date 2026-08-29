# mdms_master :  This database handles the core operational data for smart meter, consumer details, organization master (circle, subdivision,divistion,section), Network master (substation, feeder, dtr).

## l_consumer_lookup : This table contains the primary information for consumers, keywords - consumer, rrnumber, consumer related details.

### Consumer_TblRefID (int): Unique internal identity number for each consumer.
### MeterLookup_TblRefId (int): FOREIGN KEY to `l_meter_lookup`. Maps the smart meter attached to the consumer.
### RRNumber (varchar): PRIMARY KEY. Unique identifier number used to identify the consumer.
### Consumer_Name (nvarchar): Name of the consumer.
### Consumer_FatherName (nvarchar): Name of the consumer's father.
### ConnectionStatus_TblRefID (smallint, Enum: `1`='connected', `2`='disconnected', `3`='permanent disconnected'): FOREIGN KEY to `m_connection_status`. Stores the connectivity state of the smart meter.
### ConnectionCategory_TblRefID (int): FOREIGN KEY to `m_connection_category`. Stores information about the consumer's tariff category.
### Consumer_Address (nvarchar): Consumer's physical address.
### Consumer_Pincode (varchar): Consumer's postal pincode.
### Consumer_MobileNumber (varchar): Consumer's mobile phone number.
### Consumer_Email (varchar): Consumer's email address.
### Account_ID (varchar): Unique installation number for the consumer.
### Sanctioned_Load_KW (decimal): Sanctioned electrical load of the consumer (in kW).
### PaymentContract_TblRefID (int, Enum: `1`='postpaid', `2`='prepaid'): FOREIGN KEY to `m_paymenttype_contract`. Defines the consumer's payment type.
### Nearest_AccountID (varchar): Nearest account ID. If prefixed with 'NSC', it denotes a New Service Connection.
### SL_TYPE_ID (smallint): FOREIGN KEY to `m_sl_type`. Unit of measurement for sanctioned load and contract demand.
### Contract_Demand (decimal): Contract demand of the consumer.
### isPrevilege (tinyint, Enum: `0`='No', `1`='Yes'): Indicates if the consumer has privilege status (exempt from disconnection).
### Privilege_StartDate (date): Start date of the privilege period (applicable when isPrevilege = 1).
### Privilege_Enddate (date): End date of the privilege period (applicable when isPrevilege = 1).
### isStagger (tinyint, Enum: `0`='No', `1`='Yes'): Indicates if the consumer has a staggered disconnection schedule.
### Stagger_Start_date (datetime): Start date of the stagger period (applicable when isStagger = 1).
### Stagger_End_date (datetime): End date of the stagger period (applicable when isStagger = 1).
### Installment (float): Installment amount to be deducted daily.
### InstallmentStartDate (date): Start date from which the daily installment deduction begins.
### InstallmentEndDate (date): End date when the installment deduction stops.
### Installment_Received_DateTime (datetime): Date and time when the latest installment details were received.
### isForceDisconnect (tinyint, Enum: `0`='No', `1`='Yes'): Indicates if the consumer is marked for forced disconnection.
### ForceDisconnectDateTime (datetime): Date and time when the consumer was force-disconnected (applicable when isForceDisconnect = 1).
### EntryTimeStamp (datetime): Timestamp when the consumer was created in the system.
### isTOD (tinyint, Enum: `0`='No', `1`='Yes'): Indicates if Time of Day (TOD) billing is enabled for the consumer.
### MRU (varchar): Name of the Meter Reading Unit to which the consumer belongs.
### MasterSyncDate (datetime): Date and time when the consumer master sync was received from the utility/discom.
### RC_DC_DateTime (datetime): Date and time when the consumer's smart meter was last connected (RC) or disconnected (DC).
### ServiceDate (datetime): Date and time when the consumer's first smart meter was installed.
### isLRCF (bit, Enum: `0`='No', `1`='Yes'): Indicates if Local Relay Connect Functionality is enabled (null is treated as No).
### LRCF_UpdateDateTime (datetime): Date and time when LRCF was enabled (applicable when isLRCF = 1).
### Area_Type (varchar, Enum: `NON-RAPDRP`, `RAPDRP`): Defines the area type of the consumer.
### Connection_Type (varchar, Enum: `Permanent`, `Temporary`): Defines the nature of the consumer's connection.
### LoadType (varchar, Enum: `SanctionLoad`, `ContractDemand`): Defines the load type category of the consumer.
### Discom_Push_Date (datetime): Date and time when the meter installation details were pushed to the utility/discom.
### accntstatus_tblrefid (int, Enum: `1`='regular (CD)', `2`='temporary disconnected (TD)', `3`='permanent disconnected (PD)'): Stores the current account status of the consumer.

## l_meter_lookup : This table contains the hardware records for all smart meters in the system which are active or inactive. It tracks the physical properties (manufacturer, phase, meter type), configuration (multiplying factor, net metering), and logical mappings to consumers, networks, and organizations.

### MeterLookup_TblRefID (int): PRIMARY KEY. Unique internal identity number for each smart meter.
### Consumer_TblRefID (int): FOREIGN KEY to `l_consumer_lookup`. Maps the smart meter to its attached consumer.
### Meter_Serial_Number (varchar): Unique serial number of the smart meter.
### HESID (smallint): FOREIGN KEY to `m_hes`. Maps the meter to its corresponding Head-End System (HES).
### ServicePointMeterPhase_TblRefID (int): FOREIGN KEY to `m_servicepoint_meterphase`. Stores the phase configuration of the smart meter.
### DeviceManufacturer_TblRefID (int): FOREIGN KEY to `m_device_manufacturer`. Stores the manufacturer of the smart meter.
### NetworkLookup_TblRefID (int): FOREIGN KEY to `l_network_lookup`. Maps the smart meter to its parent network (generally the DTR Network).
### OrganisationLookup_TblRefID (int): FOREIGN KEY to `l_organisation_lookup`. Maps the smart meter to its specific organizational hierarchy.
### MF (float): Stores the multiplying factor (MF) of the smart meter.
### IsActiveStatus (bit, Enum: `0`='No', `1`='Yes'): Indicates if the meter is currently in an active state.
### IsNetMeter (bit, Enum: `0`='No', `1`='Yes'): Indicates whether the smart meter functions as a net meter.
### netmeter_change_ts (datetime): Date and time when the net meter function was enabled in the smart meter.
### InstallationDate (datetime): Date and time when the smart meter was physically installed.
### MeterType_TblRefID (int, Enum: `1`='feeder meter', `2`='DT meter', `3`='consumer meter'): FOREIGN KEY to `m_meter_type`. Defines the physical placement or type of the smart meter.

## l_network_lookup : This table contains the records for all electrical network entities (such as Substations, Feeders, and Distribution Transformer (DTR) networks). It defines the strict physical hierarchy of the grid, including how lower-level networks connect to higher-level networks and which utility organizations manage them.

### NetworkLookup_TblRefID (int): PRIMARY KEY. Unique internal identity number for each network entity.
### Network_Code (varchar): Standard identifier code for the network.
### Network_RAPDRPCode (varchar): RAPDRP-specific identifier code for the network.
### Network_Name (nvarchar): Name of the network entity.
### Network_Address (nvarchar): Physical address or location of the network entity.
### HigherNetwork_ID (int): FOREIGN KEY to `l_network_lookup` (Self-referencing). Maps the network to its parent or higher-level network entity.
### NetworkHierarchy_TblRefID (int, Enum: `1`='substation', `2`='feeder', `3`='dtr'): FOREIGN KEY to `m_network_hierarchy`. Defines the type of network and its level in the physical hierarchy.
### OrganisationLookup_TblRefID (int): FOREIGN KEY to `l_organisation_lookup`. Maps the network to the specific organization or office that manages it.
### IsActiveStatus (bit, Enum: `0`='No', `1`='Yes'): Indicates if the network entity is currently active.
### SUPPLY_VTG_TblRefID (int, Enum: `1`='11kv', `2`='33kv'): Stores the supply voltage capacity for the network.

## l_organisation_lookup : This table contains the records for all utility organizations and offices (such as Circle, Division, Subdivision, and Section). It defines the strict hierarchy of these offices and how they nest within one another.

### OrganisationLookup_TblRefID (int): PRIMARY KEY. Unique internal identity number for each organization/office.
### Office_Code (varchar): Unique code assigned to the organization or office.
### Office_Name (nvarchar): Name of the organization or office.
### HigherOffice_ID (int): FOREIGN KEY to `l_organisation_lookup` (Self-referencing). Maps the organization to its parent or higher-level organization.
### OrganisationHierarchy_TblRefID (int): FOREIGN KEY to `m_organisation_hierarchy`. Stores the organization type and determines its level in the hierarchy (e.g., 1 being the top-level hierarchy, followed by subsequent numbers for lower levels).
### IsActiveStatus (bit, Enum: `0`='No', `1`='Yes'): Indicates if the organization is currently in an active state.

## m_connection_category : This master lookup table defines the specific tariff codes and categorizations applied to consumers. It acts as the source of truth for classifying connections into business groups such as Domestic, Commercial, Agriculture, and Industrial.

### ConnectionCategory_TblRefID (int, Enum: `1`='KJ', `2`='KJ_BPL_MTR', `3`='DS1', `4`='DS1D', `5`='DS2D', `6`='DS3D', `7`='NDS1', `8`='NDS-IID(A)', `9`='NDS2D', `10`='LTIS1D', `11`='LTIS2D', `12`='IAS1', `13`='IAS2', `14`='PWWD', `15`='HGN', `16`='SS1D', `17`='LTEV', `18`='NDS1D', `19`='IAS2D'): PRIMARY KEY. Unique identifier for the connection category.
### ConnectionCategory_Code (varchar): UNIQUE. The standard shorthand code for the connection category (matches the ID enums).
### ConnectionCategory_Desc (varchar, Enum: `Kuteer Jyoti`, `Domestic`, `Commercial`, `LT Industrial`, `Agriculture`, `Public Water Works`, `Har Ghar Nal`, `Street Light`, `EV Charging`): The full descriptive name and classification of the connection category.

## m_connection_status : This master lookup table defines the available connectivity statuses for a consumer's smart meter. It is used to filter consumers who are currently receiving power versus those who have been temporarily or permanently disconnected.

### ConnectionStatus_TblRefID (smallint, Enum: `1`='Connected', `2`='Disconnected', `3`='Permanent Disconnection'): PRIMARY KEY. Unique identifier for the connectivity state.
### ConnectionStatus_Name (varchar, Enum: `Connected`, `Disconnected`, `Permanent Disconnection`): The full descriptive name of the connectivity state.

## m_device_manufacturer : This master lookup table stores the complete list of authorized manufacturers and brands for smart meters and related hardware devices in the system. 

### DeviceManufacturer_TblRefID (int, Enum: `1`='UTILITY', `2`='ACS', `3`='ADME', `4`='AEW', `5`='AI', `8`='AMTL', `9`='ANSHU', `10`='ANZU', `11`='ARON', `12`='ASSLTO', `13`='AT', `14`='AVON', `15`='AYONPCFR', `16`='BAJAJ', `17`='BEM', `18`='B-E-M', `19`='BENTEC', `20`='BENTEK', `21`='BENTEX', `22`='BHEL', `23`='BHM', `24`='BM', `25`='BPL', `26`='C and H', `27`='CLASS', `28`='DASS', `29`='DCD', `30`='DH', `31`='DLMS', `32`='DTRMETER', `33`='DUKE', `34`='DUMMY', `35`='EAW', `36`='EC', `37`='ECE', `38`='ELYMER', `39`='EMCO', `40`='EMLT', `41`='FERRANTI', `42`='FL', `43`='FLAP', `44`='FLASH', `45`='FLESH', `46`='FNUS', `47`='GE', `48`='GENUS', `49`='GM', `50`='GPI', `51`='GTIS', `52`='HAITEK', `53`='HARIYANA', `54`='HARYANA', `55`='HAVELLS', `56`='HEV', `57`='HI', `58`='HM', `59`='HPL', `60`='HSM', `61`='HT', `62`='HYTECH', `63`='IB', `64`='IGM', `65`='IM', `66`='INDIA', `67`='INDO FRANC', `68`='INDOTECH', `69`='IT', `70`='JAIPUR', `71`='JS,Baroda', `72`='L and G', `73`='LANDIS', `77`='LASEN', `78`='LENKAR', `81`='LINKWELL', `83`='LPT', `85`='LW', `86`='M and I', `87`='MADRAS', `88`='MANGAL', `89`='MBM', `90`='MGI', `91`='MI', `92`='MIG', `93`='MONTAIL', `94`='MONTEL', `95`='MONTEX', `96`='MOTRAL', `97`='MPVY', `98`='NACODA', `99`='NAK', `100`='NAKODA', `101`='NAMTECH', `102`='NEL', `103`='NKD', `104`='NM', `105`='PAL', `106`='PALMOAN', `107`='PALMOHA', `108`='PALMOHAN', `109`='PM', `110`='QTY', `111`='RC', `112`='REKKON', `113`='REMCO', `114`='RIKKEN', `115`='S', `116`='SCHLUMBERG', `120`='SECURE', `121`='SEMI COND', `123`='SIMCO', `124`='SINTEX', `125`='SOCOMEC', `126`='SOMAC', `128`='TGL', `129`='TLG', `130`='TOBRA', `131`='TRINCRGN', `132`='TTL', `133`='TURBO', `134`='UE', `135`='UNILAC', `136`='UNILEC', `137`='UNILIC', `138`='UNITED', `139`='UNIVERSAL', `140`='UNMETERED', `141`='UTAKE', `142`='VINOTEK', `143`='VISION', `144`='VISIONTAK', `145`='VISIONTAKE', `146`='VISIONTEC', `147`='VISIONTEK', `148`='VISIONTEX', `149`='VISNTEC', `150`='VISONTEK', `151`='VISTEC', `152`='VISTON', `153`='VS', `154`='VT', `155`='VTEK', `156`='VXL', `157`='VZS', `158`='WAATHOUR', `159`='WINNER', `160`='WPANLRAF', `162`='SARAL', `163`='GENRETION', `166`='L&T', `167`='Ametek', `168`='EL SEWEDY', `169`='GENTEK', `170`='INDIA PVT LTD', `171`='MAXWELL INDIA', `172`='PAL MOHAN', `173`='PLUTUS', `174`='POWER TECH', `175`='RMC INDIA', `176`='SEMI CONDUCTOR', `177`='SUNSTAR', `178`='VISION TECH', `179`='SCHNEIDER', `180`='OMNI AGATE', `181`='ISKRAEMECO', `261`='SWITCH GEAR', `262`='SEIPL', `263`='Capital', `301`='Kimbal', `302`='Sona Electricals Bhopal', `303`='Vishal Transformer and Switch gears'): PRIMARY KEY. Unique identifier for the device manufacturer.
### Manufacturer_Name (nvarchar): The full descriptive name of the device manufacturer.
### isActive (bit, Enum: `0`='No', `1`='Yes'): Indicates if the manufacturer is currently active and approved for use.

## m_hes : This master lookup table defines the various Head-End Systems (HES) integrated into the MDMS. The HES is the central software that communicates directly with the smart meters to collect readings and push configurations.

### HESID (smallint, Enum: `1`='Scaler', `2`='LT AMR', `3`='HT AMR', `4`='HES-Cyan', `5`='Esya', `6`='HES-BCITs', `7`='HES-Genus', `8`='Crystal-2', `9`='LnG', `10`='Schneider-HES', `11`='Genus-HES', `12`='Genus-HES2', `13`='Ashoka-HES', `14`='BCITS- HES2', `15`='Ashoka-HES2'): PRIMARY KEY. Unique identifier for the Head-End System.
### HESNAME (varchar): The descriptive name of the Head-End System software or vendor.
### IsActiveStatus (bit, Enum: `0`='No', `1`='Yes'): Indicates whether this Head-End System is currently active and supported in the environment.

## m_network_hierarchy : This master lookup table defines the specific tiers within the electrical grid's physical hierarchy. It is used to categorize network entities into top-level Substations, mid-level Feeders, and edge-level Distribution Transformers (DTRs).

### NetworkHierarchy_TblRefID (int, Enum: `1`='Sub Station', `2`='Feeder', `3`='DTR'): PRIMARY KEY. Unique identifier for the network hierarchy level.
### NetworkHierarchy_Code (varchar): Standard numeric code representing the hierarchy level.
### NetworkHierarchy_Name (nvarchar, Enum: `Sub Station`, `Feeder`, `DTR`): The descriptive name of the network tier.
### IsActiveStatus (bit, Enum: `0`='No', `1`='Yes'): Indicates whether this network hierarchy level is currently active in the system.

## m_organisation_hierarchy : This master lookup table defines the specific tiers within the utility's organizational structure. It is used to categorize offices into a strict hierarchy, where `1` represents the highest level (Headquarters) and subsequent numbers represent lower operational branches down to the Section level.

### OrganisationHierarchy_TblRefID (int, Enum: `1`='HQ', `2`='Circle', `3`='Division', `4`='Subdivision', `5`='Section'): PRIMARY KEY. Unique identifier for the organizational hierarchy level.
### OrganisationHierarchy_Code (varchar): Standard code representing the organizational level.
### OrganisationHierarchy_Name (varchar, Enum: `HQ`, `Circle`, `Division`, `Subdivision`, `Section`): The descriptive name of the organizational tier.
### IsActiveStatus (bit, Enum: `0`='No', `1`='Yes'): Indicates whether this organizational hierarchy level is currently active in the system.

##  m_paymenttype_contract :  This master lookup table defines the available payment contract types for consumers. It is primarily used to distinguish between Prepaid and Postpaid accounts across the system.

### PaymentContract_TblRefID (int, Enum: `1`='Postpaid', `2`='Prepaid'): PRIMARY KEY. Unique identifier for the payment contract type.
### PaymentContract_Name (varchar, Enum: `Postpaid`, `Prepaid`): The descriptive name of the payment contract.

## m_servicepoint_meterphase : This master lookup table defines the available physical phase configurations and connection types for smart meters across the system. It helps differentiate between standard single-phase residential meters, three-phase commercial/industrial meters, and High Tension (HT) connections.

### ServicePointMeterPhase_TblRefID (int, Enum: `1`='1 PH', `2`='3PH WC', `3`='3PH LT CT', `4`='HT', `6`='3PH LT CT'): PRIMARY KEY. Unique identifier for the meter phase configuration.
### MeterPhase_Name (varchar, Enum: `1 PH`, `3PH WC`, `3PH LT CT`, `HT`): The standard descriptive name of the meter phase.
### IsActive (bit, Enum: `0`='No', `1`='Yes'): Indicates whether this phase configuration is currently active in the system.

## m_sl_type : This master lookup table defines the units of electrical power measurement used to represent a consumer's Sanctioned Load or Contract Demand. It ensures standardized calculations across different connection types.

### SL_TYPE_ID (smallint, Enum: `1`='KW', `2`='KVA', `3`='HP', `4`='W'): PRIMARY KEY. Unique identifier for the sanctioned load unit of measurement.
### SL_TYPE_NAME (varchar, Enum: `KW`, `KVA`, `HP`, `W`): The standard abbreviation/name of the electrical power unit.

# Prepaid : This database manages the financial and operational lifecycle of prepaid consumers. It tracks daily wallet balances, applies daily energy and fixed charge deductions, records consumer recharges, and automates remote disconnection/reconnection (DC/RC) commands based on available wallet funds.

## s_meter_commanddetails : This table stores the history and status of automated meter commands triggered by the prepaid module. Specifically, it tracks Disconnection (DC) commands when a consumer's wallet balance drops too low, and Reconnection (RC) commands when the balance is restored. It monitors the lifecycle of these commands including retries and final execution statuses from the Head-End System (HES).

### TblRefID (bigint): Unique internal identity number for each command record.
### CommandRequest_TblRefID (varchar): Unique command request identifier used for tracking. If `NULL`, the command is logged but has not yet been triggered/sent to the meter.
### MeterLookup_TblRefID (bigint): PRIMARY KEY (Composite). FOREIGN KEY to `mdms_master.dbo.l_meter_lookup` (and by extension `mdms_master.dbo.l_consumer_lookup`).
### MSN (varchar): Unique Meter Serial Number associated with the consumer.
### Command_TblRefID (int, Enum: `32`='DC (Disconnection)', `33`='RC (Reconnection)'): PRIMARY KEY (Composite). Identifier dictating the type of command being executed.
### EntryDateTime (datetime): Timestamp when the command record was generated.
### IsProcessed (smallint, Enum: `0`='Pending', `1`='Processed'): Indicates whether the command has been processed by the system.
### Processed_TimeStamp (datetime): Timestamp when the command's processing was completed.
### ProcessStatus (varchar, Enum: `success`, `mansuccess`, `relsuccess`, `fail`): The final outcome of the command execution (only applicable when `IsProcessed` = 1).
### RetryCount (int): The total number of times the system has retried executing the command.
### LastRetryDateTime (datetime): Timestamp of the most recent retry attempt.
### Command_date (date): PRIMARY KEY (Composite). The date when the command was initially triggered.
### HESID (int): FOREIGN KEY to `mdms_master.dbo.m_hes`. Maps the command to the specific Head-End System responsible for the meter.
### AvailableBalance (float): The consumer's available prepaid wallet balance at the exact time the command was triggered.

## t_dailyconsumption : This table stores the daily prepaid account summaries for consumers. It tracks daily and monthly energy consumption, captures wallet balances (opening and available), and records all daily financial deductions including energy charges, fixed charges, meter rent, and installments.


### DPTblRefID (bigint): Unique internal identity number for the prepaid account record.
### EntryDateTime (datetime): Timestamp when the prepaid account record for the current day was entered into the system.
### Consumer_TblRefID (bigint): FOREIGN KEY to `mdms_master.dbo.l_consumer_lookup`. Maps the prepaid account record to the consumer.
### RRNumber (varchar): Unique identifier (account number) associated with the consumer.
### MeterLookup_TblRefID (bigint): PRIMARY KEY (Composite). FOREIGN KEY to `mdms_master.dbo.l_meter_lookup`. 
### ConsumptionDate (date): PRIMARY KEY (Composite). The specific date this prepaid account/consumption record represents.
### MSN (varchar): PRIMARY KEY (Composite). Unique Meter Serial Number associated with the consumer.
### SL (float): Sanctioned load of the consumer.
### ConnectionCategory_TblRefID (int): FOREIGN KEY to `mdms_master.dbo.m_connection_category`. Maps to the consumer's tariff category.
### installment (float): Installment amount scheduled to be deducted.
### DayNo (int): The day number of the consumer's billing cycle (resets every month).
### daykWh (float): Consumer's energy consumption for the day in kWh.
### daykVAh (float): Consumer's energy consumption for the day in kVAh.
### monthkWh (float): Consumer's accumulated energy consumption for the month in kWh.
### monthkVAh (float): Consumer's accumulated energy consumption for the month in kVAh.
### dayConsumption (float): Billed consumption for the day (metric defined by the `Unit` column).
### monthConsumption (float): Accumulated billed consumption for the month.
### MeterReading_TimeStamp (datetime): Timestamp of the last received daily profile readings.
### previousReadingkWh (float): Last recorded kWh reading.
### presentReadingkWh (float): Current day's kWh reading.
### previousReadingkVAh (float): Last recorded kVAh reading.
### presentReadingkVAh (float): Current day's kVAh reading.
### isProcessed (smallint, Enum: `-1`='DP not received', `0`='DP received, consumptions updated', `1`='Calculation completed'): Processing status of the prepaid account for the day.
### processedTimeStamp (datetime): Timestamp when the `isProcessed` status was last updated.
### dayEnergyCharge (float): Energy charges deducted for the day.
### dayFixedCharge (float): Fixed charges deducted for the day.
### dayMeterRent (float): Meter rent deducted for the day.
### dayInstallment (float): Installment amount deducted for the day.
### DayOpeningBalance (float): Consumer's opening wallet balance for the day.
### totalAvailableAmount (float): Consumer's current available wallet balance.
### dayCreditAdjust (float): Amount credited to the consumer's wallet during the day.
### dayDebitAdjust (float): Amount debited from the consumer's wallet during the day.
### billdaybalance (float): Consumer's opening wallet balance on the 1st day of the billing month.
### isdpmissing (int, Enum: `0`='No', `1`='Yes'): Flag indicating if the daily profile (DP) is missing for the current day.
### last_dp_date (date): The date of the last successfully received daily profile (DP).
### MonthEnergyCharge (float): Accumulated energy charges deducted for the month.
### MonthFixedCharge (float): Accumulated fixed charges deducted for the month.
### MonthMeterRent (float): Accumulated meter rent deducted for the month.
### MonthInstallment (float): Accumulated installments deducted for the month.
### SettlementDeductedAmount (float): Total settlement amount deducted (negative value indicates credit, positive value indicates debit).
### SettlementOutstandingAmount (float): Total outstanding settlement amount (negative value indicates credit, positive value indicates debit).
### virtual_cr (float): Virtual credit received in a day.
### virtual_dr (float): Virtual debit received in a day.
### Inv_CreditAmount (float): Amount credited via invoice.
### Inv_DebitAmount (float): Amount debited via invoice.
### ArrearOutstandingAmount (float): Outstanding installment amount for the current month.
### Total_ArrearOutstandingAmt (float): Total overall outstanding installment amount.
### dayED (float): Electricity Duty (ED) charges deducted for the day.
### dayGovtSubsidy (float): Government subsidy credited/applied for the day.
### dayRebate (float): Rebate amount applied for the day.
### monthED (float): Accumulated Electricity Duty (ED) charges for the month.
### monthGovtSubsidy (float): Accumulated government subsidy for the month.
### monthRebate (float): Accumulated rebate amount for the month.
### Unit (varchar, Enum: `KWH`, `KVAH`): Specifies the unit of measurement used to calculate the prepaid charges.

## t_dailyconsumption_arch : This is the archival history table for `t_dailyconsumption`. It stores historical daily prepaid account summaries for consumers for past days. It tracks past daily and monthly energy consumption, historical wallet balances, and records all previous daily financial deductions (energy charges, fixed charges, meter rent, and installments).

### DPTblRefID (bigint): Unique internal identity number for the prepaid account record.
### EntryDateTime (datetime): Timestamp when the prepaid account record was entered into the system.
### Consumer_TblRefID (bigint): FOREIGN KEY to `mdms_master.l_consumer_lookup`. Maps the prepaid account record to the consumer.
### RRNumber (varchar): Unique identifier (account number) associated with the consumer.
### MeterLookup_TblRefID (bigint): PRIMARY KEY (Composite). FOREIGN KEY to `mdms_master.l_meter_lookup`. 
### ConsumptionDate (date): PRIMARY KEY (Composite). The specific historical date this prepaid account/consumption record represents.
### MSN (varchar): PRIMARY KEY (Composite). Unique Meter Serial Number associated with the consumer.
### SL (float): Sanctioned load of the consumer.
### ConnectionCategory_TblRefID (int): FOREIGN KEY to `mdms_master.m_connection_category`. Maps to the consumer's tariff category.
### installment (float): Installment amount scheduled to be deducted.
### DayNo (int): The day number of the consumer's billing cycle (resets every month).
### daykWh (float): Consumer's energy consumption for the day in kWh.
### daykVAh (float): Consumer's energy consumption for the day in kVAh.
### monthkWh (float): Consumer's accumulated energy consumption for the month in kWh.
### monthkVAh (float): Consumer's accumulated energy consumption for the month in kVAh.
### dayConsumption (float): Billed consumption for the day (metric defined by the `Unit` column).
### monthConsumption (float): Accumulated billed consumption for the month.
### MeterReading_TimeStamp (datetime): Timestamp of the last received daily profile readings.
### previousReadingkWh (float): Last recorded kWh reading.
### presentReadingkWh (float): Current day's kWh reading.
### previousReadingkVAh (float): Last recorded kVAh reading.
### presentReadingkVAh (float): Current day's kVAh reading.
### isProcessed (smallint, Enum: `-1`='DP not received', `0`='DP received, consumptions updated', `1`='Calculation completed'): Processing status of the prepaid account for the day.
### processedTimeStamp (datetime): Timestamp when the `isProcessed` status was last updated.
### dayEnergyCharge (float): Energy charges deducted for the day.
### dayFixedCharge (float): Fixed charges deducted for the day.
### dayMeterRent (float): Meter rent deducted for the day.
### dayInstallment (float): Installment amount deducted for the day.
### DayOpeningBalance (float): Consumer's opening wallet balance for the day.
### totalAvailableAmount (float): Consumer's current available wallet balance.
### dayCreditAdjust (float): Amount credited to the consumer's wallet during the day.
### dayDebitAdjust (float): Amount debited from the consumer's wallet during the day.
### billdaybalance (float): Consumer's opening wallet balance on the 1st day of the billing month.
### isdpmissing (int, Enum: `0`='No', `1`='Yes'): Flag indicating if the daily profile (DP) was missing for this historical day.
### last_dp_date (date): The date of the last successfully received daily profile (DP).
### MonthEnergyCharge (float): Accumulated energy charges deducted for the month.
### MonthFixedCharge (float): Accumulated fixed charges deducted for the month.
### MonthMeterRent (float): Accumulated meter rent deducted for the month.
### MonthInstallment (float): Accumulated installments deducted for the month.
### SettlementDeductedAmount (float): Total settlement amount deducted (negative value indicates credit, positive value indicates debit).
### SettlementOutstandingAmount (float): Total outstanding settlement amount (negative value indicates credit, positive value indicates debit).
### virtual_cr (float): Virtual credit received in a day.
### virtual_dr (float): Virtual debit received in a day.
### Inv_CreditAmount (float): Amount credited via invoice.
### Inv_DebitAmount (float): Amount debited via invoice.
### ArrearOutstandingAmount (float): Outstanding installment amount for the month.
### Total_ArrearOutstandingAmt (float): Total overall outstanding installment amount.
### dayED (float): Electricity Duty (ED) charges deducted for the day.
### dayGovtSubsidy (float): Government subsidy credited/applied for the day.
### dayRebate (float): Rebate amount applied for the day.
### monthED (float): Accumulated Electricity Duty (ED) charges for the month.
### monthGovtSubsidy (float): Accumulated government subsidy for the month.
### monthRebate (float): Accumulated rebate amount for the month.
### Unit (varchar, Enum: `KWH`, `KVAH`): Specifies the unit of measurement used to calculate the prepaid charges.

## t_payment : This table records all financial inflow/recharge events for consumer prepaid wallets. It captures the transaction amounts, dates, and the specific source of the recharge (e.g., whether the consumer paid via the mobile app/portal or if the recharge was processed through the discom's internal billing system). 

### PMT_TblRefID (bigint): Unique internal identity number for the payment record.
### EntryDateTime (datetime): Timestamp when the payment record was entered into the system.
### Consumer_TblRefid (bigint): FOREIGN KEY to `mdms_master.dbo.l_consumer_lookup`. Maps the payment to the consumer.
### MeterLookup_TblRefID (bigint): FOREIGN KEY to `mdms_master.dbo.l_meter_lookup`. Maps the payment to the specific smart meter.
### RequestID (varchar): Unique request identifier associated with the recharge request.
### RRNumber (varchar): Unique identifier (number) associated with the consumer.
### InstallationNumber (varchar): Installation number associated with the consumer/meter setup.
### RechargeAmount (numeric): The financial amount credited to the prepaid wallet during this transaction.
### txnID (varchar): PRIMARY KEY. Unique transaction ID for the recharge (this column also stores the discom transaction ID).
### RechargeDate (datetime): The date and time when the recharge was successfully processed.
### AmountAtLastRecharge (numeric): The wallet balance amount immediately prior to this recharge being applied.
### txnSource_TblRefid (int, Enum: `1`='discom/utility/rms/billing system', `2`='consumer app/portal'): Indicates the origin or source platform of the recharge transaction.
### UtilityReceiptNumber (varchar): Receipt number generated by the utility's internal billing system, if applicable.

