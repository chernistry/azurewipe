"""Network resource cleaners (NICs, Public IPs, NSGs)."""
import logging
from typing import List, Dict, Any
from azure.mgmt.network import NetworkManagementClient
from azure.core.credentials import TokenCredential
from azurewipe.core.config import Config
from azurewipe.core.graph import ResourceGraphQuery
from azurewipe.core.retry import retry_with_backoff
from .base import ResourceCleaner


class NICCleaner(ResourceCleaner):
    resource_type = "nic"
    dependencies = ["vm"]

    def __init__(self, credential: TokenCredential, config: Config):
        super().__init__(credential, config)
        self.graph = ResourceGraphQuery(credential)

    def discover(self, subscriptions: List[str]) -> List[Dict[str, Any]]:
        logging.info("Discovering orphan NICs...")
        nics = self.graph.find_orphan_nics(subscriptions)
        logging.info(f"Found {len(nics)} orphan NICs")
        return nics

    @retry_with_backoff()
    def delete(self, resource: Dict[str, Any]) -> bool:
        sub_id = resource["subscriptionId"]
        rg = resource["resourceGroup"]
        name = resource["name"]

        logging.info(f"Deleting NIC {name}")
        try:
            client = NetworkManagementClient(self.credential, sub_id)
            poller = client.network_interfaces.begin_delete(rg, name)
            poller.result()
            return True
        except Exception as e:
            logging.error(f"Failed to delete NIC {name}: {e}")
            return False


class PublicIPCleaner(ResourceCleaner):
    resource_type = "publicip"
    dependencies = ["nic", "vm"]

    def __init__(self, credential: TokenCredential, config: Config):
        super().__init__(credential, config)
        self.graph = ResourceGraphQuery(credential)

    def discover(self, subscriptions: List[str]) -> List[Dict[str, Any]]:
        logging.info("Discovering unused Public IPs...")
        ips = self.graph.find_unused_public_ips(subscriptions)
        logging.info(f"Found {len(ips)} unused Public IPs")
        return ips

    @retry_with_backoff()
    def delete(self, resource: Dict[str, Any]) -> bool:
        sub_id = resource["subscriptionId"]
        rg = resource["resourceGroup"]
        name = resource["name"]

        logging.info(f"Deleting Public IP {name}")
        try:
            client = NetworkManagementClient(self.credential, sub_id)
            poller = client.public_ip_addresses.begin_delete(rg, name)
            poller.result()
            return True
        except Exception as e:
            logging.error(f"Failed to delete Public IP {name}: {e}")
            return False


class NSGCleaner(ResourceCleaner):
    resource_type = "nsg"
    dependencies = ["nic"]

    def __init__(self, credential: TokenCredential, config: Config):
        super().__init__(credential, config)
        self.graph = ResourceGraphQuery(credential)

    def discover(self, subscriptions: List[str]) -> List[Dict[str, Any]]:
        logging.info("Discovering unused NSGs...")
        nsgs = self.graph.find_unused_nsgs(subscriptions)
        logging.info(f"Found {len(nsgs)} unused NSGs")
        return nsgs

    @retry_with_backoff()
    def delete(self, resource: Dict[str, Any]) -> bool:
        sub_id = resource["subscriptionId"]
        rg = resource["resourceGroup"]
        name = resource["name"]

        logging.info(f"Deleting NSG {name}")
        try:
            client = NetworkManagementClient(self.credential, sub_id)
            poller = client.network_security_groups.begin_delete(rg, name)
            poller.result()
            return True
        except Exception as e:
            logging.error(f"Failed to delete NSG {name}: {e}")
            return False
