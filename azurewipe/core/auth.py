"""Azure authentication utilities."""
from azure.identity import DefaultAzureCredential, AzureCliCredential
from azure.core.credentials import TokenCredential


def get_credential() -> TokenCredential:
    """Get Azure credential using DefaultAzureCredential chain.
    
    Tries in order: Environment → Managed Identity → Azure CLI → Interactive
    """
    return DefaultAzureCredential()


def get_cli_credential() -> TokenCredential:
    """Get credential from Azure CLI (az login)."""
    return AzureCliCredential()
