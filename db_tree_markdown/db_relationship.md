## l_consumer_lookup : The central entity is `l_consumer_lookup` (Alias: lcl).

### Target: `l_meter_lookup` (Alias: lml) , Join Logic: `lcl.MeterLookup_TblRefId = lml.MeterLookup_TblRefID` , Purpose: Links one consumer to their primary installed smart meter.

### Target: `m_connection_status` (Alias: mcs) , Join Logic: `lcl.ConnectionStatus_TblRefID = mcs.ConnectionStatus_TblRefID` , Purpose: Gets the physical connectivity/relay status.

### Target: `m_connection_category` (Alias: mcc) , Join Logic: `lcl.ConnectionCategory_TblRefID = mcc.ConnectionCategory_TblRefID` , Purpose: Gets the consumer's tariff/category (e.g., Domestic, Commercial).

### Target: `m_paymenttype_contract` (Alias: mptc) , Join Logic: `lcl.PaymentContract_TblRefID = mptc.PaymentContract_TblRefID` , Purpose: Identifies if the consumer is Prepaid or Postpaid.

### Target: `m_sl_type` (Alias: mslt) , Join Logic: `lcl.SL_TYPE_ID = mslt.SL_TYPE_ID` , Purpose: Gets the unit of measurement for sanctioned load.


## l_meter_lookup (Alias: lml) to define hardware specs and physical locations.

### Target: `m_hes` (Alias: mhes) , Join Logic: `lml.HESID = mhes.HESID` , Purpose: Maps the meter to its communicating Head-End System.

### Target: `m_servicepoint_meterphase` (Alias: msmp) , Join Logic: `lml.ServicePointMeterPhase_TblRefID = msmp.ServicePointMeterPhase_TblRefID` , Purpose: Gets the physical phase (1 Phase, 3 Phase, etc.).

### Target: `m_device_manufacturer` (Alias: mdm) , Join Logic: `lml.DeviceManufacturer_TblRefID = mdm.DeviceManufacturer_TblRefID` , Purpose: Identifies the smart meter's brand/manufacturer.

### Target: `l_network_lookup` (Alias: lnl) , Join Logic: `lml.NetworkLookup_TblRefID = lnl.NetworkLookup_TblRefID` , Purpose: Maps the smart meter to its parent network (usually a DTR).

### Target: `l_organisation_lookup` (Alias: l_org) , Join Logic: `lml.OrganisationLookup_TblRefID = l_org.OrganisationLookup_TblRefID` , Purpose: Maps the smart meter to its managing utility office.


## l_network_lookup : Network Hierarchy and Self-Joins

### Target: `l_organisation_lookup` (Alias: l_org) , Join Logic: `l_network_lookup.OrganisationLookup_TblRefID = l_organisation_lookup.OrganisationLookup_TblRefID`

### Target: `m_network_hierarchy` , Join Logic: `l_network_lookup.NetworkHierarchy_TblRefID = m_network_hierarchy.NetworkHierarchy_TblRefID`

### Target: `l_network_lookup` (Self-Join: Parent/Child) , Join Logic: `child_net.HigherNetwork_ID = parent_net.NetworkLookup_TblRefID` , Purpose: E.g., Finding the Feeder for a specific DTR.


## l_organisation_lookup : Organisation Hierarchy and Self-Joins

### Target: `m_organisation_hierarchy` , Join Logic: `l_organisation_lookup.OrganisationHierarchy_TblRefID = m_organisation_hierarchy.OrganisationHierarchy_TblRefID`

### Target: `l_organisation_lookup` (Self-Join: Parent/Child) , Join Logic: `child_org.HigherOffice_ID = parent_org.OrganisationLookup_TblRefID` , Purpose: E.g., Finding the Division for a specific Subdivision.

## t_dailyconsumption : Daily Consumption Joins

### Target: `prepaid.dbo.t_dailyconsumption_arch` (Alias: tdca) , Join Logic: `tdc.Consumer_TblRefID = tdca.Consumer_TblRefID`

### Target: `mdms_master.dbo.l_consumer_lookup` (Alias: lcl) , Join Logic: `tdc.Consumer_TblRefID = lcl.Consumer_TblRefID`

### Target: `mdms_master.dbo.m_connection_category` (Alias: mcc) , Source: `prepaid.dbo.t_dailyconsumption` (Alias: tdc) and `prepaid.dbo.t_dailyconsumption_arch` (Alias: tdca) , Join Logic: `tdc.ConnectionCategory_TblRefID = mcc.ConnectionCategory_TblRefID` , Purpose: Identifies the tariff category under which the daily charges were calculated.

## t_dailyconsumption_arch : Archive Consumption Joins

### Target: `mdms_master.dbo.l_consumer_lookup` (Alias: lcl) , Join Logic: `tdca.Consumer_TblRefID = lcl.Consumer_TblRefID`

## t_payment : Payment Joins

### Target: `mdms_master.dbo.l_consumer_lookup` (Alias: lcl) , Source: `prepaid.dbo.t_payment` (Alias: tp) , Join Logic: `tp.Consumer_TblRefid = lcl.Consumer_TblRefID` , Purpose: Links a recharge/payment to the consumer who made it.

### Target: `mdms_master.dbo.l_meter_lookup` (Alias: lml) , Source: `prepaid.dbo.t_payment` (Alias: tp) , Join Logic: `tp.MeterLookup_TblRefID = lml.MeterLookup_TblRefID` , Purpose: Links the recharge to the specific smart meter.


## s_meter_commanddetails : Meter Command Details Joins

### Target: `mdms_master.dbo.l_meter_lookup` (Alias: lml) , Source: `prepaid.dbo.s_meter_commanddetails` (Alias: smcd) , Join Logic: `smcd.MeterLookup_TblRefID = lml.MeterLookup_TblRefID` , Purpose: Identifies which meter the command was issued against.

### Target: `mdms_master.dbo.m_hes` (Alias: mhes) , Source: `prepaid.dbo.s_meter_commanddetails` (Alias: smcd) , Join Logic: `smcd.HESID = mhes.HESID` , Purpose: Identifies which Head-End System was responsible for executing the command.