from types import SimpleNamespace as NS
from unittest.mock import patch

import inventory


def named(name: str):
    return NS(metadata=NS(name=name))


def in_namespace(namespace: str):
    return NS(metadata=NS(namespace=namespace))


def test_inventory_filters_resources_by_cloud():
    with patch.object(inventory, "config"), patch.object(inventory, "client") as client:
        client.CoreV1Api.return_value.list_namespace.return_value.items = [
            named("aws-dev"), named("gcp-dev"), named("default"),
        ]
        client.CoreV1Api.return_value.list_pod_for_all_namespaces.return_value.items = [
            in_namespace("aws-dev"), in_namespace("aws-dev"), in_namespace("gcp-dev"),
        ]
        client.AppsV1Api.return_value.list_deployment_for_all_namespaces.return_value.items = [
            in_namespace("aws-dev"), in_namespace("gcp-dev"),
        ]

        result = inventory.get_inventory("aws", "kind-aws")

    assert result == {"cloud": "aws", "namespaces": ["aws-dev"], "pods": 2, "deployments": 1}
