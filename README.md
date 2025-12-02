# AzureWipe

Automated Azure resource cleanup tool. Deletes orphaned resources across all subscriptions and regions, reduces costs, maintains account hygiene.

Azure equivalent of [awswipe](https://github.com/chernistry/awswipe).

## Why

- Dev/test subscriptions accumulate unused resources
- Orphaned disks, NICs, and public IPs cost money
- Manual cleanup is tedious and error-prone
- Azure doesn't auto-delete your forgotten infrastructure

## Features

| Feature | Description |
|---------|-------------|
| Multi-subscription | Cleans all Azure subscriptions in parallel |
| Safe by default | Dry-run mode, tag filtering, exclude patterns |
| Comprehensive | VMs, Storage, VNets, AKS, Functions, SQL, and more |
| Configurable | YAML config or CLI flags |
| Observable | Structured JSON logging, detailed reports |
| Interactive | TUI menu for common operations |

## Installation

```bash
git clone https://github.com/chernistry/azurewipe.git
cd azurewipe
pip install -r requirements.txt
```

Requires Python 3.10+ and Azure CLI (`az login`).

## Usage

```bash
# Dry-run (default) - see what would be deleted
python azurewipe.py

# Interactive menu
python azurewipe.py -i

# Delete everything in specific subscription
python azurewipe.py --subscription <id> --live-run

# Delete specific resource group
python azurewipe.py --resource-group dev-rg --live-run

# Use config file
python azurewipe.py --config config.yaml
```

## Configuration

```yaml
subscriptions:
  - <subscription-id>

resource_groups:
  - dev-*
  - test-*

tag_filters:
  include:
    Environment: [dev, test]
  exclude:
    DoNotDelete: ["true"]

dry_run: true
```

## License

MIT

## Author

Alexander Chernysh — [GitHub](https://github.com/chernistry)
