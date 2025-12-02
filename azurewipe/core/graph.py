"""Azure Resource Graph queries for resource discovery."""
import logging
from typing import List, Dict, Any, Optional
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest, QueryRequestOptions
from azure.mgmt.resource import SubscriptionClient
from azure.core.credentials import TokenCredential

# KQL queries for orphaned resources
QUERIES = {
    "unattached_disks": """
        Resources
        | where type =~ 'microsoft.compute/disks'
        | where managedBy == '' or isnull(managedBy)
        | where properties.diskState =~ 'Unattached'
        | project id, name, resourceGroup, subscriptionId, location, tags
    """,
    "orphan_nics": """
        Resources
        | where type =~ 'microsoft.network/networkinterfaces'
        | where isnull(properties.virtualMachine)
        | project id, name, resourceGroup, subscriptionId, location, tags
    """,
    "unused_public_ips": """
        Resources
        | where type =~ 'microsoft.network/publicipaddresses'
        | where isnull(properties.ipConfiguration)
        | project id, name, resourceGroup, subscriptionId, location, tags
    """,
    "unused_nsgs": """
        Resources
        | where type =~ 'microsoft.network/networksecuritygroups'
        | where isnull(properties.networkInterfaces) or array_length(properties.networkInterfaces) == 0
        | where isnull(properties.subnets) or array_length(properties.subnets) == 0
        | project id, name, resourceGroup, subscriptionId, location, tags
    """,
    "all_vms": """
        Resources
        | where type =~ 'microsoft.compute/virtualmachines'
        | project id, name, resourceGroup, subscriptionId, location, tags, properties
    """,
    "empty_resource_groups": """
        ResourceContainers
        | where type =~ 'microsoft.resources/subscriptions/resourcegroups'
        | join kind=leftouter (
            Resources | summarize count() by resourceGroup, subscriptionId
        ) on $left.name == $right.resourceGroup and $left.subscriptionId == $right.subscriptionId
        | where isnull(count_) or count_ == 0
        | project id, name, subscriptionId, location, tags
    """,
}


class ResourceGraphQuery:
    """Azure Resource Graph client wrapper."""

    def __init__(self, credential: TokenCredential):
        self.credential = credential
        self.graph_client = ResourceGraphClient(credential)
        self.subscription_client = SubscriptionClient(credential)

    def list_subscriptions(self) -> List[str]:
        """List all accessible subscription IDs."""
        subs = []
        for sub in self.subscription_client.subscriptions.list():
            if sub.state == "Enabled":
                subs.append(sub.subscription_id)
        logging.info(f"Found {len(subs)} enabled subscriptions")
        return subs

    def query(
        self,
        query: str,
        subscriptions: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute a Resource Graph query with pagination."""
        if subscriptions is None:
            subscriptions = self.list_subscriptions()

        results = []
        skip_token = None

        while True:
            options = QueryRequestOptions(
                result_format="objectArray",
                skip_token=skip_token,
            )
            request = QueryRequest(
                subscriptions=subscriptions,
                query=query,
                options=options,
            )
            response = self.graph_client.resources(request)
            results.extend(response.data)

            skip_token = response.skip_token
            if not skip_token:
                break

        return results

    def find_unattached_disks(self, subscriptions: Optional[List[str]] = None) -> List[Dict]:
        return self.query(QUERIES["unattached_disks"], subscriptions)

    def find_orphan_nics(self, subscriptions: Optional[List[str]] = None) -> List[Dict]:
        return self.query(QUERIES["orphan_nics"], subscriptions)

    def find_unused_public_ips(self, subscriptions: Optional[List[str]] = None) -> List[Dict]:
        return self.query(QUERIES["unused_public_ips"], subscriptions)

    def find_unused_nsgs(self, subscriptions: Optional[List[str]] = None) -> List[Dict]:
        return self.query(QUERIES["unused_nsgs"], subscriptions)

    def find_all_vms(self, subscriptions: Optional[List[str]] = None) -> List[Dict]:
        return self.query(QUERIES["all_vms"], subscriptions)

    def find_empty_resource_groups(self, subscriptions: Optional[List[str]] = None) -> List[Dict]:
        return self.query(QUERIES["empty_resource_groups"], subscriptions)
