from azure.storage.blob import BlobServiceClient, ContainerClient


def get_container_client(storage_url: str, storage_cred_key: str, container_name: str) -> ContainerClient:
    """
    A helper function that returns Azure Storage ContainerClient. Necessary as reusing Client is potentially
    thread-unsafe. Creates a container with container_name if not found.

    :param storage_url: URL to Azure Storage account
    :param storage_cred_key: Azure Storage account access key
    :param container_name: Name of the container to use
    :return: Container Client for Azure Storage SDK
    """
    c: BlobServiceClient = BlobServiceClient(account_url=storage_url, credential=storage_cred_key)

    for b in c.list_containers():
        if b.name == container_name:
            return c.get_container_client(container_name)
    return c.create_container(container_name, public_access="blob")
