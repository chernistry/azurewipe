"""Resource cleaners for Azure."""
from .base import ResourceCleaner
from .disk import DiskCleaner
from .network import NICCleaner, PublicIPCleaner, NSGCleaner
from .vm import VMCleaner
from .resource_group import ResourceGroupCleaner

CLEANERS = {
    "disk": DiskCleaner,
    "nic": NICCleaner,
    "publicip": PublicIPCleaner,
    "nsg": NSGCleaner,
    "vm": VMCleaner,
    "resource_group": ResourceGroupCleaner,
}
