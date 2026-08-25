# Database: mdms_master (Core consumer profiles, statuses, contact details, and payment types)

## Tables

### Table: m_paymenttype_contract (Master lookup for payment contract types)
#### Column: PaymentContract_TblRefID (Unique Payment Contract ID)
- **Data Type:** int
- **Constraint:** PRIMARY KEY
- **Enums:** 1 = Postpaid, 2 = Prepaid
- **Description:** Unique identifier for the payment contract type.

#### Column: PaymentContract_Name (Payment Contract Name)
- **Data Type:** varchar
- **Enums:** Postpaid, Prepaid
- **Description:** The descriptive name of the payment contract.

### Table: l_consumer_lookup (Consumer master records, attributes, and settings)
#### Column: Consumer_TblRefID (Internal Consumer ID)
- **Data Type:** int
- **Description:** Unique internal identity number for each consumer.

#### Column: MeterLookup_TblRefId (Smart Meter Reference)
- **Data Type:** int
- **Constraint:** Foreign Key
- **Description:** Maps the smart meter attached to the consumer.

#### Column: RRNumber (Consumer ID / Account Number)
- **Data Type:** varchar
- **Constraint:** PRIMARY KEY
- **Description:** Unique identifier number used to identify the consumer.

#### Column: Consumer_Name (Consumer Name)
- **Data Type:** nvarchar
- **Description:** Name of the consumer.

#### Column: Consumer_FatherName (Father's Name)
- **Data Type:** nvarchar
- **Description:** Name of the consumer's father.

#### Column: ConnectionStatus_TblRefID (Connectivity State)
- **Data Type:** smallint
- **Constraint:** Foreign Key
- **Enums:** 1 = Connected, 2 = Disconnected, 3 = Permanent Disconnected
- **Description:** Stores the connectivity state of the smart meter.

#### Column: ConnectionCategory_TblRefID (Tariff Category Reference)
- **Data Type:** int
- **Constraint:** Foreign Key
- **Description:** Stores information about the consumer's tariff category.

#### Column: Consumer_Address (Physical Address)
- **Data Type:** nvarchar
- **Description:** Consumer's physical address.

#### Column: Consumer_Pincode (Postal Pincode)
- **Data Type:** varchar
- **Description:** Consumer's postal pincode.

#### Column: Consumer_MobileNumber (Mobile Phone Number)
- **Data Type:** varchar
- **Description:** Consumer's mobile phone number.

#### Column: Consumer_Email (Email Address)
- **Data Type:** varchar
- **Description:** Consumer's email address.

#### Column: Account_ID (Installation Number)
- **Data Type:** varchar
- **Description:** Unique installation number for the consumer.

#### Column: Sanctioned_Load_KW (Sanctioned Load)
- **Data Type:** decimal
- **Description:** Sanctioned electrical load of the consumer (in kW).

#### Column: PaymentContract_TblRefID (Payment Mode Reference)
- **Data Type:** int
- **Constraint:** Foreign Key
- **Enums:** 1 = Postpaid, 2 = Prepaid
- **Description:** Defines the consumer's payment type.

#### Column: Nearest_AccountID (Nearest Account Identifier)
- **Data Type:** varchar
- **Description:** Nearest account ID. If prefixed with 'NSC', it denotes a New Service Connection.

#### Column: SL_TYPE_ID (Sanctioned Load Unit Reference)
- **Data Type:** smallint
- **Constraint:** Foreign Key
- **Description:** Unit of measurement for sanctioned load and contract demand.

#### Column: Contract_Demand (Contract Demand Value)
- **Data Type:** decimal
- **Description:** Contract demand of the consumer.

#### Column: isPrevilege (Privilege Status Indicator)
- **Data Type:** tinyint
- **Enums:** 0 = No, 1 = Yes
- **Description:** Indicates if the consumer has privilege status (exempt from disconnection).

#### Column: Privilege_StartDate (Privilege Start Date)
- **Data Type:** date
- **Description:** Start date of the privilege period (applicable when isPrevilege = 1).

#### Column: Privilege_Enddate (Privilege End Date)
- **Data Type:** date
- **Description:** End date of the privilege period (applicable when isPrevilege = 1).

#### Column: isStagger (Stagger Disconnection Schedule Indicator)
- **Data Type:** tinyint
- **Enums:** 0 = No, 1 = Yes
- **Description:** Indicates if the consumer has a staggered disconnection schedule.

#### Column: Stagger_Start_date (Stagger Schedule Start Date)
- **Data Type:** datetime
- **Description:** Start date of the stagger period (applicable when isStagger = 1).

#### Column: Stagger_End_date (Stagger Schedule End Date)
- **Data Type:** datetime
- **Description:** End date of the stagger period (applicable when isStagger = 1).

#### Column: Installment (Daily Deduction Installment Amount)
- **Data Type:** float
- **Description:** Installment amount to be deducted daily.

#### Column: InstallmentStartDate (Installment Start Date)
- **Data Type:** date
- **Description:** Start date from which the daily installment deduction begins.

#### Column: InstallmentEndDate (Installment End Date)
- **Data Type:** date
- **Description:** End date when the installment deduction stops.

#### Column: Installment_Received_DateTime (Installment Details Timestamp)
- **Data Type:** datetime
- **Description:** Date and time when the latest installment details were received.

#### Column: isForceDisconnect (Forced Disconnection Indicator)
- **Data Type:** tinyint
- **Enums:** 0 = No, 1 = Yes
- **Description:** Indicates if the consumer is marked for forced disconnection.

#### Column: ForceDisconnectDateTime (Forced Disconnection Timestamp)
- **Data Type:** datetime
- **Description:** Date and time when the consumer was force-disconnected (applicable when isForceDisconnect = 1).

#### Column: EntryTimeStamp (Record Creation Timestamp)
- **Data Type:** datetime
- **Description:** Timestamp when the consumer was created in the system.

#### Column: isTOD (Time of Day Billing Indicator)
- **Data Type:** tinyint
- **Enums:** 0 = No, 1 = Yes
- **Description:** Indicates if Time of Day (TOD) billing is enabled for the consumer.

#### Column: MRU (Meter Reading Unit)
- **Data Type:** varchar
- **Description:** Name of the Meter Reading Unit to which the consumer belongs.

#### Column: MasterSyncDate (Utility Sync Timestamp)
- **Data Type:** datetime
- **Description:** Date and time when the consumer master sync was received from the utility/discom.

#### Column: RC_DC_DateTime (Reconnection / Disconnection Timestamp)
- **Data Type:** datetime
- **Description:** Date and time when the consumer's smart meter was last connected (RC) or disconnected (DC).

#### Column: ServiceDate (First Installation Timestamp)
- **Data Type:** datetime
- **Description:** Date and time when the consumer's first smart meter was installed.

#### Column: isLRCF (Local Relay Connect Functionality Indicator)
- **Data Type:** bit
- **Enums:** 0 = No, 1 = Yes
- **Description:** Indicates if Local Relay Connect Functionality is enabled (null is treated as No).

#### Column: LRCF_UpdateDateTime (LRCF Enablement Timestamp)
- **Data Type:** datetime
- **Description:** Date and time when LRCF was enabled (applicable when isLRCF = 1).

#### Column: Area_Type (Area Classification)
- **Data Type:** varchar
- **Enums:** NON-RAPDRP, RAPDRP
- **Description:** Defines the area type of the consumer.

#### Column: Connection_Type (Connection Nature)
- **Data Type:** varchar
- **Enums:** Permanent, Temporary
- **Description:** Defines the nature of the consumer's connection.

#### Column: LoadType (Load Type Classification)
- **Data Type:** varchar
- **Enums:** SanctionLoad, ContractDemand
- **Description:** Defines the load type category of the consumer.

#### Column: Discom_Push_Date (Discom Push Timestamp)
- **Data Type:** datetime
- **Description:** Date and time when the meter installation details were pushed to the utility/discom.

#### Column: accntstatus_tblrefid (Current Account Status)
- **Data Type:** int
- **Enums:** 1 = Regular (CD), 2 = Temporary Disconnected (TD), 3 = Permanent Disconnected (PD)
- **Description:** Stores the current account status of the consumer.

## Relationships (Foreign Keys and Join Logic)

### Join: l_consumer_lookup to m_paymenttype_contract
- **Target Table:** m_paymenttype_contract
- **Join Logic:** l_consumer_lookup.PaymentContract_TblRefID = m_paymenttype_contract.PaymentContract_TblRefID
- **Purpose:** Identifies if the consumer is Prepaid or Postpaid.