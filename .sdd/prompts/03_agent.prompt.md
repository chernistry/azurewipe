# Agent Prompt Template

You are the Implementing Agent (CLI/IDE). Work strictly from specifications.

Project Context:
- Project: azurewipe
- Stack: Python/Azure SDK/Azure CLI
- Domain: cloud-infrastructure
- Year: 2025
- Reference: awswipe (/Users/sasha/IdeaProjects/personal_projects/awswipe)

Required reading (use fs_read to access):
- `.sdd/project.md` — project description
- `.sdd/best_practices.md` — research and best practices
- `.sdd/architect.md` — architecture specification
- `.sdd/backlog/tickets/open/` — tickets sorted by prefix

Operating rules:
- **Always consult architect.md** first.
- **Execute backlog tasks by dependency order.**
- **Write minimal viable code (MVP)** with tests.
- **Mirror awswipe patterns** where applicable.
- **Respect formatters, linters, and conventions.**
- **Keep diffs minimal.**

## Azure-Specific Guidelines

### Authentication
```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

credential = DefaultAzureCredential()
client = ResourceManagementClient(credential, subscription_id)
```

### Resource Discovery (Azure Resource Graph)
```python
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest

query = "Resources | where type == 'microsoft.compute/virtualmachines'"
request = QueryRequest(subscriptions=[sub_id], query=query)
response = client.resources(request)
```

### Deletion Pattern
```python
# Always check for locks first
locks = lock_client.management_locks.list_at_resource_level(...)
if locks:
    logging.warning(f"Resource {id} has locks, skipping")
    return

# Delete with polling
poller = compute_client.virtual_machines.begin_delete(rg, vm_name)
poller.result()  # Wait for completion
```

### Soft Delete Handling
```python
# Key Vault - purge after soft delete
keyvault_client.vaults.begin_purge_deleted(vault_name, location)

# Storage - check soft delete settings
storage_client.blob_services.get_service_properties(rg, account)
```

## Per‑task process
1) Read ticket and verify DoD
2) Check awswipe for reference implementation
3) Adapt for Azure SDK
4) Add tests
5) Run lint/type checks

## Quality Gates
- Build succeeds
- mypy passes
- ruff/black clean
- Tests green
- No secrets in code

## Git Hygiene
- Branch: `feat/<ticket-id>-<slug>`
- Commits: Conventional Commits
