"""AzureWipe CLI entry point."""
import argparse
import logging
import time
from azurewipe.core.config import load_config
from azurewipe.core.logging import setup_logging, get_run_id


def parse_args():
    parser = argparse.ArgumentParser(description="AzureWipe - Azure Resource Cleanup Tool")
    parser.add_argument("--config", "-c", help="Path to YAML config file")
    parser.add_argument("--subscription", "-s", help="Subscription ID (overrides config)")
    parser.add_argument("--resource-group", "-g", help="Resource group (overrides config)")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Verbosity: -v=INFO, -vv=DEBUG")
    parser.add_argument("--json-logs", action="store_true", help="Output logs in JSON format")
    parser.add_argument("--live-run", action="store_true", help="Actually delete resources (default: dry-run)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive menu mode")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.interactive:
        from azurewipe.interactive import run_interactive
        run_interactive()
        return

    config = load_config(args.config)

    if args.subscription:
        config.subscriptions = [args.subscription]
    if args.resource_group:
        config.resource_groups = [args.resource_group]
    if args.verbose:
        config.verbosity = args.verbose
    if args.json_logs:
        config.json_logs = True
    if args.live_run:
        config.dry_run = False

    setup_logging(config.verbosity, config.json_logs)
    logging.info(f"AzureWipe run_id={get_run_id()} dry_run={config.dry_run}")

    from azurewipe.cleaner import AzureResourceCleaner
    cleaner = AzureResourceCleaner(config)

    if not config.dry_run:
        logging.warning("LIVE RUN MODE - Resources WILL be deleted")
        try:
            for i in range(5, 0, -1):
                print(f"Starting in {i}s... (Ctrl+C to cancel)", end="\r")
                time.sleep(1)
            print(" " * 40, end="\r")
        except KeyboardInterrupt:
            logging.info("Cancelled by user")
            return

    cleaner.purge()


if __name__ == "__main__":
    main()
