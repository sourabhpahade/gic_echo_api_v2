---
type: Table
title: l_organisation_lookup
description: Core table storing the organizational hierarchy, mapping offices, their codes, and relationships to higher-level organizations.
database: mdms_master
default_alias: l_org
tags: 
- organisation
- hierarchy
- office
- division
- section
---

# Table: l_organisation_lookup

## Description
This table contains the records for all utility organizations and offices (such as Circle, Division, Subdivision, and Section). It defines the strict hierarchy of these offices and how they nest within one another.

## Columns
* **OrganisationLookup_TblRefID** (int): PRIMARY KEY. Unique internal identity number for each organization/office.
* **Office_Code** (varchar): Unique code assigned to the organization or office.
* **Office_Name** (nvarchar): Name of the organization or office.
* **HigherOffice_ID** (int): FOREIGN KEY to `l_organisation_lookup` (Self-referencing). Maps the organization to its parent or higher-level organization.
* **OrganisationHierarchy_TblRefID** (int): FOREIGN KEY to `m_organisation_hierarchy`. Stores the organization type and determines its level in the hierarchy (e.g., 1 being the top-level hierarchy, followed by subsequent numbers for lower levels).
* **IsActiveStatus** (bit, Enum: `0`='No', `1`='Yes'): Indicates if the organization is currently in an active state.