# Relationship

## l_consumer_lookup : The central entity is `l_consumer_lookup` (Alias: lcl).
    
### Target: `l_meter_lookup` (Alias: lml) , Join Logic: `lcl.MeterLookup_TblRefId = lml.MeterLookup_TblRefID`
### Target: `m_connection_status` (Alias: mcs)  Join Logic: `lcl.ConnectionStatus_TblRefID = mcs.ConnectionStatus_TblRefID`
### Target: `m_connection_category` (Alias: mcc) Join Logic: `lcl.ConnectionCategory_TblRefID = mcc.ConnectionCategory_TblRefID`
### Target: `m_paymenttype_contract` (Alias: mptc) Join Logic: `lcl.PaymentContract_TblRefID = mptc.PaymentContract_TblRefID`
### Target: `m_sl_type` (Alias: mslt) Join Logic: `lcl.SL_TYPE_ID = mslt.SL_TYPE_ID`

## l_meter_lookup (Alias: lml) to define hardware specs and physical locations.

### Target: `m_hes` (Alias: mhes) , Join Logic: `lml.HESID = mhes.HESID`
### Target: `m_servicepoint_meterphase` (Alias: msmp) , Join Logic: `lml.ServicePointMeterPhase_TblRefID = msmp.ServicePointMeterPhase_TblRefID`
### Target: `m_device_manufacturer` (Alias: mdm) , Join Logic: `lml.DeviceManufacturer_TblRefID = mdm.DeviceManufacturer_TblRefID`
### Target: `l_network_lookup` (Alias: lnl) , Join Logic: `lml.NetworkLookup_TblRefID = lnl.NetworkLookup_TblRefID`
### Target: `l_organisation_lookup` (Alias: l_org) , Join Logic: `lml.OrganisationLookup_TblRefID = l_org.OrganisationLookup_TblRefID`

