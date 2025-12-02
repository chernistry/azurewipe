"""Empty Resource Group cleaner."""
import logging
from typing import List, Dict, Any
from azure.mgmt.resource import ResourceManagementClient
from azure.core.credentials import TokenCredential
from azurewipe.core.config import Config
from azurewipe.core.graph import ResourceGraphQuery
from azurewipe.core.retry import retry_with_backoff
from .base import ResourceCleaner


class ResourceGroupCleaner(ResourceCleaner):
    resource_type = "resource_group"
    dependencies = ["vm", "disk", "nic", "publicip", "nsg"]  # Delete last

    def __init__(self, credential: TokenCredential, config: Config):
        super().__init__(credential, config)
        self.graph = ResourceGraphQuery(credential)

    def discover(self, subscriptions: List[str]) -> List[Dict[str, Any]]:
        logging.info("Discovering empty Resource Groups...")
        rgs = self.graph.find_empty_resource_groups(subscriptions)
        logging.info(f"Found {len(rgs)} empty Resource Groups")
        return rgs

    @retry_with_backoff()
    def delete(self, resource: Dict[str, Any]) -> bool:
        sub_id = resource["subscriptionId"]
        name = resource["name"]

        logging.info(f"Deleting Resource Group {name}")
        try:
            client = ResourceManagementClient(self.credential, sub_id)
            poller = client.resource_groups.begin_delete(name)
            poller.result()
            return True
        except Exception as e:
            logging.error(f"Failed to delete RG {name}: {e}")
            return False
