---
type: Table
title: m_organisation_hierarchy
description: Master lookup table defining the structural levels of the utility's organization (e.g., HQ, Circle, Division, Subdivision, Section).
database: mdms_master
default_alias: moh
tags: 
- organisation hierarchy
- circle
- division
- subdivision
- section
---

# Table: m_organisation_hierarchy

## Description
This master lookup table defines the specific tiers within the utility's organizational structure. It is used to categorize offices into a strict hierarchy, where `1` represents the highest level (Headquarters) and subsequent numbers represent lower operational branches down to the Section level.

## Columns
* **OrganisationHierarchy_TblRefID** (int, Enum: `1`='HQ', `2`='Circle', `3`='Division', `4`='Subdivision', `5`='Section'): PRIMARY KEY. Unique identifier for the organizational hierarchy level.
* **OrganisationHierarchy_Code** (varchar): Standard code representing the organizational level.
* **OrganisationHierarchy_Name** (varchar, Enum: `HQ`, `Circle`, `Division`, `Subdivision`, `Section`): The descriptive name of the organizational tier.
* **IsActiveStatus** (bit, Enum: `0`='No', `1`='Yes'): Indicates whether this organizational hierarchy level is currently active in the system.