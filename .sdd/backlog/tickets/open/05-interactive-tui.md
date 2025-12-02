# Ticket: 05 Interactive TUI

Spec version: v1.0

## User Problem
- Need user-friendly interactive menu like awswipe

## Outcome / Success Signals
- `azurewipe -i` launches Textual TUI
- Menu options for common operations

## Objective & Definition of Done
- [ ] interactive.py with Textual app
- [ ] Menu: Preview, Nuke subscription, Nuke RG, Clean by type, Custom
- [ ] Confirmation dialogs
- [ ] Subscription/RG selection screens

## Steps
1. Copy and adapt interactive.py from awswipe
2. Replace AWS-specific options with Azure equivalents
3. Add subscription selector
4. Add resource group selector
5. Test TUI flow

## Affected files/modules
- `azurewipe/interactive.py`

## Menu Options
1. Preview (dry-run)
2. Nuke subscription
3. Nuke resource group
4. Clean compute only (VMs, disks)
5. Clean networking only (NICs, IPs, NSGs)
6. Custom selection
7. Exit

## Dependencies
- Upstream: 04-cleaner
- Downstream: none
