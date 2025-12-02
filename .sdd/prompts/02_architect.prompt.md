# Architect Prompt Template

Instruction for AI: based on the project description and best practices, prepare an implementation‑ready architecture specification.

Context:
- Project: azurewipe
- Description: see `.sdd/project.md`
- Domain: cloud-infrastructure
- Tech stack: Python/Azure SDK/Azure CLI/Bicep
- Year: 2025
- Best practices: see `.sdd/best_practices.md`
- Reference implementation: awswipe (see /Users/sasha/IdeaProjects/personal_projects/awswipe)

---

## Task
Produce architect.md as the source of truth for implementation. Mirror the structure of awswipe but adapted for Azure.

## Output Structure (Markdown)

### Scope Analysis Summary
- Appetite: [Small/Batch/Big]
- Key Constraints: [List]

### Goals & Non‑Goals
- Goals: Mirror awswipe functionality for Azure
- Non‑Goals: [List]

### Architecture Overview
```
azurewipe/
├── __init__.py
├── cli.py              # argparse, main()
├── cleaner.py          # AzureResourceCleaner (orchestration)
├── interactive.py      # Textual TUI
├── core/
│   ├── __init__.py
│   ├── retry.py        # retry with backoff
│   ├── logging.py      # structured JSON logging
│   └── config.py       # YAML config loader
└── resources/
    ├── __init__.py
    ├── base.py         # ResourceCleaner ABC
    ├── vm.py           # Virtual Machines
    ├── storage.py      # Storage Accounts
    ├── network.py      # VNets, NICs, NSGs, Public IPs
    ├── aks.py          # AKS clusters
    ├── functions.py    # Azure Functions
    ├── sql.py          # Azure SQL, CosmosDB
    └── keyvault.py     # Key Vaults (soft delete handling)
```

### Key Decisions (ADR‑style)
- [ADR‑001] Use Azure SDK (azure-mgmt-*) over CLI for programmatic control
- [ADR‑002] Use Azure Resource Graph for discovery (efficient, cross-subscription)
- [ADR‑003] Three-phase deletion: discover → tag → delete
- [ADR‑004] Handle soft-delete for Storage, Key Vault, etc.

### Resource Types to Support
1. Compute: VMs, VMSS, AKS, Container Instances, Functions
2. Storage: Storage Accounts, Disks, Snapshots, Blobs
3. Network: VNets, Subnets, NICs, NSGs, Public IPs, Load Balancers, App Gateways
4. Database: Azure SQL, CosmosDB, PostgreSQL, MySQL
5. Identity: Service Principals, Managed Identities (careful!)
6. Other: Key Vaults, App Services, Logic Apps, Event Hubs

### Dependency Graph (deletion order)
```
VMs → Disks → Snapshots
VMs → NICs → Public IPs
AKS → Node Pools → VMs
VNets → Subnets → NICs
Resource Groups (last, if empty)
```

### Code Standards
- Python 3.10+
- Type hints (mypy strict)
- black, ruff for formatting/linting
- pytest for tests
- Structured JSON logging

### CLI Interface
```bash
# Dry-run (default)
python azurewipe.py

# Interactive TUI
python azurewipe.py -i

# Specific subscription
python azurewipe.py --subscription <id>

# Specific resource group
python azurewipe.py --resource-group <name>

# Live run
python azurewipe.py --live-run

# With config
python azurewipe.py --config config.yaml
```

### Configuration (YAML)
```yaml
subscriptions:
  - <subscription-id>
  # or "all"

resource_groups:
  - dev-*
  - test-*

resource_types:
  - vm
  - storage
  - network

tag_filters:
  include:
    Environment: [dev, test]
  exclude:
    DoNotDelete: ["true"]

exclude_patterns:
  - "prod-*"

dry_run: true
json_logs: false
```

### Backlog (Tickets)
Create tickets in `.sdd/backlog/tickets/open/`:
- 01-project-setup.md
- 02-core-modules.md
- 03-azure-auth.md
- 04-resource-discovery.md
- 05-vm-cleaner.md
- 06-storage-cleaner.md
- 07-network-cleaner.md
- 08-interactive-tui.md
- 09-config-and-cli.md
- 10-testing.md
