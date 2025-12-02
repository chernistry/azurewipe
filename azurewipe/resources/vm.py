"""Virtual Machine cleaner."""
import logging
from typing import List, Dict, Any
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ManagementLockClient
from azure.core.credentials import TokenCredential
from azurewipe.core.config import Config
from azurewipe.core.graph import ResourceGraphQuery
from azurewipe.core.retry import retry_with_backoff
from .base import ResourceCleaner


class VMCleaner(ResourceCleaner):
    resource_type = "vm"
    dependencies = []

    def __init__(self, credential: TokenCredential, config: Config):
        super().__init__(credential, config)
        self.graph = ResourceGraphQuery(credential)

    def discover(self, subscriptions: List[str]) -> List[Dict[str, Any]]:
        logging.info("Discovering VMs...")
        vms = self.graph.find_all_vms(subscriptions)
        logging.info(f"Found {len(vms)} VMs")
        return vms

    def _has_lock(self, sub_id: str, rg: str, name: str) -> bool:
        """Check if VM has a delete lock."""
        try:
            lock_client = ManagementLockClient(self.credential, sub_id)
            locks = lock_client.management_locks.list_at_resource_level(
                rg, "Microsoft.Compute", "", "virtualMachines", name
            )
            for lock in locks:
                if lock.level in ("CanNotDelete", "ReadOnly"):
                    return True
        except Exception:
            pass
        return False

    @retry_with_backoff()
    def delete(self, resource: Dict[str, Any]) -> bool:
        sub_id = resource["subscriptionId"]
        rg = resource["resourceGroup"]
        name = resource["name"]

        if self._has_lock(sub_id, rg, name):
            logging.warning(f"VM {name} has lock, skipping")
            self.report["skipped"].append(resource["id"])
            return False

        logging.info(f"Deleting VM {name}")
        try:
            client = ComputeManagementClient(self.credential, sub_id)
            poller = client.virtual_machines.begin_delete(rg, name)
            poller.result()
            return True
        except Exception as e:
            logging.error(f"Failed to delete VM {name}: {e}")
            return False
