from types import SimpleNamespace as NS
from unittest.mock import patch

import health


def node(ready: bool):
    status = "True" if ready else "False"
    return NS(status=NS(conditions=[NS(type="Ready", status=status)]))


def pod(namespace: str, phase: str = "Running"):
    return NS(metadata=NS(namespace=namespace), status=NS(phase=phase))


def check(nodes, pods, cloud="aws"):
    with patch.object(health, "config"), patch.object(health, "client") as client:
        v1 = client.CoreV1Api.return_value
        v1.list_node.return_value.items = nodes
        v1.list_pod_for_all_namespaces.return_value.items = pods
        return health.check_health(cloud, f"kind-{cloud}")


def test_healthy_when_nodes_ready_and_all_pods_running():
    result = check([node(True)], [pod("aws-dev"), pod("aws-dev")])

    assert result["healthy"] is True
    assert result["pods_running"] == 2
    assert result["pods_total"] == 2


def test_degraded_when_a_pod_is_not_running():
    result = check([node(True)], [pod("aws-dev"), pod("aws-dev", "Pending")])

    assert result["healthy"] is False
    assert result["pods_running"] == 1


def test_degraded_when_a_node_is_not_ready():
    result = check([node(True), node(False)], [pod("aws-dev")])

    assert result["node_ready"] is False
    assert result["healthy"] is False


def test_only_counts_pods_from_the_selected_cloud():
    result = check([node(True)], [pod("aws-dev"), pod("gcp-dev", "Pending"), pod("kube-system")])

    assert result["pods_total"] == 1
    assert result["healthy"] is True
