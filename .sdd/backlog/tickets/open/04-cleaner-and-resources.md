# Ticket: 04 Cleaner and Resource Modules

Spec version: v1.0

## User Problem
- Need orchestration and resource-specific deletion logic

## Outcome / Success Signals
- AzureResourceCleaner can discover and delete resources
- Each resource type has its own module

## Objective & Definition of Done
- [ ] cleaner.py - main orchestration
- [ ] resources/base.py - ABC for resource cleaners
- [ ] resources/disk.py - unattached disks
- [ ] resources/network.py - NICs, Public IPs, NSGs
- [ ] resources/vm.py - Virtual Machines
- [ ] resources/resource_group.py - empty RGs
- [ ] Dependency ordering
- [ ] Lock detection and skip

## Steps
1. Create base.py with ResourceCleaner ABC
2. Implement disk.py (simplest, good starting point)
3. Implement network.py (NICs, IPs, NSGs)
4. Implement vm.py
5. Implement resource_group.py
6. Create cleaner.py orchestration
7. Add lock detection

## Affected files/modules
- `azurewipe/cleaner.py`
- `azurewipe/resources/__init__.py`
- `azurewipe/resources/base.py`
- `azurewipe/resources/disk.py`
- `azurewipe/resources/network.py`
- `azurewipe/resources/vm.py`
- `azurewipe/resources/resource_group.py`

## Dependencies
- Upstream: 02, 03
- Downstream: 05-interactive
