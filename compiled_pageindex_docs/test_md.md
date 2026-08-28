# mdms_master : This database handles the core operational data for smart meter installations, consumer details, utility hierarchies, and the master lookup tables that define system statuses and categories.


## Tables

###  l_consumer_lookup : This table contains the primary information for consumers in the MDMS, including names, addresses, connectivity states, and physical attributes. 

#### Columns

##### Consumer_TblRefID (int): Unique internal identity number for each consumer.
##### MeterLookup_TblRefId (int): FOREIGN KEY to `l_meter_lookup`. Maps the smart meter attached to the consumer.
##### RRNumber (varchar): PRIMARY KEY. Unique identifier number used to identify the consumer.
##### Consumer_Name (nvarchar): Name of the consumer.
##### Consumer_FatherName (nvarchar): Name of the consumer's father.
##### ConnectionStatus_TblRefID (smallint, Enum: `1`='connected', `2`='disconnected', `3`='permanent disconnected'): FOREIGN KEY to `m_connection_status`. Stores the connectivity state of the smart meter.
##### ConnectionCategory_TblRefID (int): FOREIGN KEY to `m_connection_category`. Stores information about the consumer's tariff category.
##### Consumer_Address (nvarchar): Consumer's physical address.
##### Consumer_Pincode (varchar): Consumer's postal pincode.
##### Consumer_MobileNumber (varchar): Consumer's mobile phone number.
##### Consumer_Email (varchar): Consumer's email address.
##### Account_ID (varchar): Unique installation number for the consumer.
##### Sanctioned_Load_KW (decimal): Sanctioned electrical load of the consumer (in kW).
##### PaymentContract_TblRefID (int, Enum: `1`='postpaid', `2`='prepaid'): FOREIGN KEY to `m_paymenttype_contract`. Defines the consumer's payment type.
##### Nearest_AccountID (varchar): Nearest account ID. If prefixed with 'NSC', it denotes a New Service Connection.
##### SL_TYPE_ID (smallint): FOREIGN KEY to `m_sl_type`. Unit of measurement for sanctioned load and contract demand.
##### Contract_Demand (decimal): Contract demand of the consumer.
##### isPrevilege (tinyint, Enum: `0`='No', `1`='Yes'): Indicates if the consumer has privilege status (exempt from disconnection).
##### Privilege_StartDate (date): Start date of the privilege period (applicable when isPrevilege = 1).
##### Privilege_Enddate (date): End date of the privilege period (applicable when isPrevilege = 1).
##### isStagger (tinyint, Enum: `0`='No', `1`='Yes'): Indicates if the consumer has a staggered disconnection schedule.
##### Stagger_Start_date (datetime): Start date of the stagger period (applicable when isStagger = 1).
##### Stagger_End_date (datetime): End date of the stagger period (applicable when isStagger = 1).
##### Installment (float): Installment amount to be deducted daily.
##### InstallmentStartDate (date): Start date from which the daily installment deduction begins.
##### InstallmentEndDate (date): End date when the installment deduction stops.
##### Installment_Received_DateTime (datetime): Date and time when the latest installment details were received.
##### isForceDisconnect (tinyint, Enum: `0`='No', `1`='Yes'): Indicates if the consumer is marked for forced disconnection.
##### ForceDisconnectDateTime (datetime): Date and time when the consumer was force-disconnected (applicable when isForceDisconnect = 1).
##### EntryTimeStamp (datetime): Timestamp when the consumer was created in the system.
##### isTOD (tinyint, Enum: `0`='No', `1`='Yes'): Indicates if Time of Day (TOD) billing is enabled for the consumer.
##### MRU (varchar): Name of the Meter Reading Unit to which the consumer belongs.
##### MasterSyncDate (datetime): Date and time when the consumer master sync was received from the utility/discom.
##### RC_DC_DateTime (datetime): Date and time when the consumer's smart meter was last connected (RC) or disconnected (DC).
##### ServiceDate (datetime): Date and time when the consumer's first smart meter was installed.
##### isLRCF (bit, Enum: `0`='No', `1`='Yes'): Indicates if Local Relay Connect Functionality is enabled (null is treated as No).
##### LRCF_UpdateDateTime (datetime): Date and time when LRCF was enabled (applicable when isLRCF = 1).
##### Area_Type (varchar, Enum: `NON-RAPDRP`, `RAPDRP`): Defines the area type of the consumer.
##### Connection_Type (varchar, Enum: `Permanent`, `Temporary`): Defines the nature of the consumer's connection.
##### LoadType (varchar, Enum: `SanctionLoad`, `ContractDemand`): Defines the load type category of the consumer.
##### Discom_Push_Date (datetime): Date and time when the meter installation details were pushed to the utility/discom.
##### accntstatus_tblrefid (int, Enum: `1`='regular (CD)', `2`='temporary disconnected (TD)', `3`='permanent disconnected (PD)'): Stores the current account status of the consumer.

#### Relationships

##### Target:`l_meter_lookup` (Alias: lml) : Links one consumer to their primary installed smart meter. 
     **Join Logic**: `lcl.MeterLookup_TblRefId = lml.MeterLookup_TblRefID`.
