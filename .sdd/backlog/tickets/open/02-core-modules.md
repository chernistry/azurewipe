# Ticket: 02 Core Modules

Spec version: v1.0

## User Problem
- Need reusable core utilities (logging, config, retry, auth)

## Outcome / Success Signals
- Structured JSON logging works
- YAML config loads correctly
- Azure authentication works

## Objective & Definition of Done
- [ ] core/logging.py - JSON formatter, run_id
- [ ] core/config.py - YAML loader, Config dataclass
- [ ] core/retry.py - retry with exponential backoff
- [ ] core/auth.py - DefaultAzureCredential wrapper
- [ ] config.example.yaml

## Steps
1. Copy and adapt logging.py from awswipe
2. Copy and adapt config.py, add Azure-specific fields
3. Create retry.py with Azure SDK retry patterns
4. Create auth.py with credential helper

## Affected files/modules
- `azurewipe/core/__init__.py`
- `azurewipe/core/logging.py`
- `azurewipe/core/config.py`
- `azurewipe/core/retry.py`
- `azurewipe/core/auth.py`
- `config.example.yaml`

## Dependencies
- Upstream: 01-project-setup
- Downstream: 03, 04, 05
