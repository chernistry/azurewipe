# Ticket: 03 Azure Resource Graph Discovery

Spec version: v1.0

## User Problem
- Need efficient cross-subscription resource discovery

## Outcome / Success Signals
- Can query orphaned resources across subscriptions
- KQL queries for each resource type

## Objective & Definition of Done
- [ ] core/graph.py - Resource Graph client wrapper
- [ ] KQL queries for: unattached disks, orphan NICs, unused IPs, unused NSGs
- [ ] Pagination handling
- [ ] Subscription enumeration

## Steps
1. Create graph.py with ResourceGraphClient
2. Implement query method with pagination
3. Add predefined queries for orphan detection
4. Add subscription listing

## Affected files/modules
- `azurewipe/core/graph.py`

## KQL Queries
```kql
// Unattached disks
Resources
| where type =~ 'microsoft.compute/disks'
| where managedBy == '' or isnull(managedBy)
| where properties.diskState =~ 'Unattached'

// Orphan NICs
Resources
| where type =~ 'microsoft.network/networkinterfaces'
| where isnull(properties.virtualMachine)

// Unused Public IPs
Resources
| where type =~ 'microsoft.network/publicipaddresses'
| where isnull(properties.ipConfiguration)
```

## Dependencies
- Upstream: 02-core-modules
- Downstream: 04-cleaner
