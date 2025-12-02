# Ticket: 01 Project Setup

Spec version: v1.0

## User Problem
- Need basic project structure to start development

## Outcome / Success Signals
- `python -m azurewipe --help` works
- Package structure matches architect.md

## Objective & Definition of Done
- [ ] Create package structure
- [ ] requirements.txt with Azure SDK dependencies
- [ ] Basic CLI entry point
- [ ] __main__.py for `python -m azurewipe`

## Steps
1. Create azurewipe/ package directory
2. Create __init__.py, __main__.py
3. Create requirements.txt
4. Create minimal cli.py with argparse

## Affected files/modules
- `azurewipe/__init__.py`
- `azurewipe/__main__.py`
- `azurewipe/cli.py`
- `requirements.txt`

## Dependencies
- Upstream: none
- Downstream: all other tickets
