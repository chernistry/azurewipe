"""Main orchestration for Azure resource cleanup."""
import logging
from typing import Dict, List, Any
from azure.core.credentials import TokenCredential
from azurewipe.core.config import Config
from azurewipe.core.auth import get_credential
from azurewipe.core.graph import ResourceGraphQuery
from azurewipe.resources import CLEANERS


class AzureResourceCleaner:
    """Orchestrates Azure resource cleanup."""

    # Deletion order (dependencies first)
    CLEANUP_ORDER = ["vm", "disk", "nic", "publicip", "nsg", "resource_group"]

    def __init__(self, config: Config, credential: TokenCredential = None):
        self.config = config
        self.credential = credential or get_credential()
        self.graph = ResourceGraphQuery(self.credential)
        self.report: Dict[str, Dict[str, List]] = {}

    def _get_subscriptions(self) -> List[str]:
        """Get list of subscriptions to clean."""
        if "all" in self.config.subscriptions:
            return self.graph.list_subscriptions()
        return self.config.subscriptions

    def purge(self):
        """Run the cleanup process."""
        subscriptions = self._get_subscriptions()
        logging.info(f"Cleaning {len(subscriptions)} subscription(s)")

        if self.config.dry_run:
            logging.info("DRY-RUN MODE - no resources will be deleted")

        # Determine which resource types to clean
        if "all" in self.config.resource_types:
            types_to_clean = self.CLEANUP_ORDER
        else:
            types_to_clean = [t for t in self.CLEANUP_ORDER if t in self.config.resource_types]

        # Clean in dependency order
        for res_type in types_to_clean:
            if res_type not in CLEANERS:
                logging.warning(f"Unknown resource type: {res_type}")
                continue

            cleaner_class = CLEANERS[res_type]
            cleaner = cleaner_class(self.credential, self.config)
            report = cleaner.clean(subscriptions)
            self.report[res_type] = report

            deleted = len(report["deleted"])
            failed = len(report["failed"])
            skipped = len(report["skipped"])
            action = "Would delete" if self.config.dry_run else "Deleted"
            logging.info(f"{res_type}: {action} {deleted}, failed {failed}, skipped {skipped}")

        self.print_report()

    def print_report(self):
        """Print cleanup report."""
        print("\n=== Azure Cleanup Report ===")
        for res_type, results in self.report.items():
            print(f"\nResource: {res_type}")
            action = "Would delete" if self.config.dry_run else "Deleted"
            print(f"  {action}:")
            if results["deleted"]:
                for item in results["deleted"][:10]:  # Limit output
                    print(f"    - {item}")
                if len(results["deleted"]) > 10:
                    print(f"    ... and {len(results['deleted']) - 10} more")
            else:
                print("    None")
            if results["failed"]:
                print("  Failed:")
                for item in results["failed"][:5]:
                    print(f"    - {item}")
            if results["skipped"]:
                print(f"  Skipped: {len(results['skipped'])}")
