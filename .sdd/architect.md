# AzureWipe Architecture Specification

## Scope Analysis Summary
- **Appetite:** Batch
- **Key Constraints:** Safe-by-default, multi-subscription support, Python/Azure SDK
- **Reference:** awswipe structure and patterns

## Goals & Non-Goals

### Goals
1. Mirror awswipe functionality for Azure
2. Safe three-phase lifecycle: discover → quarantine → delete
3. Multi-subscription and multi-region support via Azure Resource Graph
4. Interactive TUI (Textual)
5. YAML configuration with tag filtering
6. Structured JSON logging

### Non-Goals
- Full SaaS platform
- Azure Policy management
- Cost optimization recommendations (beyond deletion)

## Architecture Overview

```
azurewipe/
├── __init__.py
├── __main__.py
├── cli.py                  # argparse, main()
├── cleaner.py              # AzureResourceCleaner orchestration
├── interactive.py          # Textual TUI
├── core/
│   ├── __init__.py
│   ├── auth.py             # Azure authentication
│   ├── retry.py            # retry with backoff
│   ├── logging.py          # structured JSON logging
│   ├── config.py           # YAML config loader
│   └── graph.py            # Azure Resource Graph queries
└── resources/
    ├── __init__.py
    ├── base.py             # ResourceCleaner ABC
    ├── vm.py               # Virtual Machines
    ├── disk.py             # Managed Disks
    ├── network.py          # NICs, NSGs, Public IPs
    ├── storage.py          # Storage Accounts
    └── resource_group.py   # Empty Resource Groups
```

## Key Decisions (ADR-style)

### ADR-001: Use Azure SDK over CLI for core logic
- **Decision:** Use azure-mgmt-* packages for all resource operations
- **Rationale:** Better testability, typed models, built-in retries
- **Trade-off:** More code than CLI, but more control

### ADR-002: Use Azure Resource Graph for discovery
- **Decision:** Primary discovery via ARG KQL queries
- **Rationale:** Efficient cross-subscription queries, single API call
- **Fallback:** SDK list APIs where ARG insufficient

### ADR-003: Three-phase deletion lifecycle
- **Decision:** discover → quarantine (tag) → delete
- **Rationale:** Safety, auditability, reversibility
- **Tags:** `azurewipe:phase`, `azurewipe:reason`, `azurewipe:since`

### ADR-004: Respect locks and soft-delete
- **Decision:** Skip locked resources, never auto-purge soft-deleted
- **Rationale:** Governance compliance, data protection

## Resource Types (MVP)

| Type | ARG Query | SDK Client | Dependencies |
|------|-----------|------------|--------------|
| VMs | `microsoft.compute/virtualmachines` | ComputeManagementClient | → Disks, NICs |
| Disks | `microsoft.compute/disks` where unattached | ComputeManagementClient | - |
| NICs | `microsoft.network/networkinterfaces` where unattached | NetworkManagementClient | → Public IPs |
| Public IPs | `microsoft.network/publicipaddresses` where unassociated | NetworkManagementClient | - |
| NSGs | `microsoft.network/networksecuritygroups` where unused | NetworkManagementClient | - |
| Storage | `microsoft.storage/storageaccounts` | StorageManagementClient | Soft-delete! |
| Resource Groups | Empty RGs | ResourceManagementClient | Last |

## Deletion Order (Dependency Graph)
```
VMs → NICs → Public IPs
VMs → Disks
NSGs (if not attached)
Storage Accounts (respect soft-delete)
Empty Resource Groups (last)
```

## Authentication Flow
```python
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
# Tries: Environment → Managed Identity → Azure CLI → Interactive
```

## Configuration Schema
```yaml
subscriptions:
  - <subscription-id>  # or "all"

resource_groups:
  - "dev-*"
  - "test-*"

resource_types:
  - vm
  - disk
  - nic
  - publicip
  - nsg
  - storage

tag_filters:
  include:
    Environment: [dev, test, sandbox]
  exclude:
    DoNotDelete: ["true"]
    azurewipe:protect: ["true"]

exclude_patterns:
  - "prod-*"

dry_run: true
json_logs: false
verbosity: 1
```

## CLI Interface
```bash
azurewipe                           # dry-run all
azurewipe -i                        # interactive TUI
azurewipe --subscription <id>       # specific subscription
azurewipe --resource-group <name>   # specific RG
azurewipe --live-run                # actually delete
azurewipe --config config.yaml      # use config file
azurewipe -v                        # verbose
azurewipe --json-logs               # JSON output
```

## Code Standards
- Python 3.10+
- Type hints everywhere (mypy strict)
- black + ruff for formatting/linting
- pytest for tests
- Structured JSON logging with run_id

## Quality Gates
- [ ] All tests pass
- [ ] mypy clean
- [ ] ruff/black clean
- [ ] No secrets in code
- [ ] Dry-run works correctly
- [ ] Locks are respected
