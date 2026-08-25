# Database System Documentation

## Database: mdms_master
Description and domain metadata for MDMS Master.

### Tables

#### Table: l_consumer_lookup
- **Description**: Master lookup table for consumer entities.
- **Primary Key**: `consumer_id`
- **Columns**:
  - `consumer_id` (INT): Unique ID.
  - `org_id` (INT): Link to organization lookup.

#### Table: l_meter_lookup
- **Description**: Master lookup table for meter hardware.
- **Primary Key**: `meter_id`
- **Columns**:
  - `meter_id` (INT): Unique ID.

### Relationships
- `l_consumer_lookup.org_id` -> `l_organisation_lookup.id` (Many-to-One)

---

## Database: prepaid
Description and domain metadata for Prepaid system.

### Tables

#### Table: t_dailyconsumption
- **Description**: Stores daily meter consumption data logs.
- **Primary Key**: `id`
- **Columns**:
  - `id` (BIGINT): Record primary key.
  - `meter_id` (INT): Foreign key matching `l_meter_lookup.meter_id`.

### Relationships
- `t_dailyconsumption.meter_id` -> `mdms_master.l_meter_lookup.meter_id` (Cross-DB Foreign Key)