"""Disk cleaner for unattached managed disks."""
import logging
from typing import List, Dict, Any
from azure.mgmt.compute import ComputeManagementClient
from azure.core.credentials import TokenCredential
from azurewipe.core.config import Config
from azurewipe.core.graph import ResourceGraphQuery
from azurewipe.core.retry import retry_with_backoff
from .base import ResourceCleaner


class DiskCleaner(ResourceCleaner):
    resource_type = "disk"
    dependencies = ["vm"]

    def __init__(self, credential: TokenCredential, config: Config):
        super().__init__(credential, config)
        self.graph = ResourceGraphQuery(credential)

    def discover(self, subscriptions: List[str]) -> List[Dict[str, Any]]:
        logging.info("Discovering unattached disks...")
        disks = self.graph.find_unattached_disks(subscriptions)
        logging.info(f"Found {len(disks)} unattached disks")
        return disks

    @retry_with_backoff()
    def delete(self, resource: Dict[str, Any]) -> bool:
        sub_id = resource["subscriptionId"]
        rg = resource["resourceGroup"]
        name = resource["name"]

        logging.info(f"Deleting disk {name} in {rg}")
        try:
            client = ComputeManagementClient(self.credential, sub_id)
            poller = client.disks.begin_delete(rg, name)
            poller.result()
            logging.info(f"Deleted disk {name}")
            return True
        except Exception as e:
            logging.error(f"Failed to delete disk {name}: {e}")
            return False
