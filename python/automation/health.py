from kubernetes import client, config
from rich.console import Console
from rich.table import Table
import datetime

CLOUDS = {
    "aws":   "kind-aws",
    "gcp":   "kind-gcp",
    "azure": "kind-azure",
}

console = Console()

def check_health(cloud: str, context: str) -> dict:
    config.load_kube_config(context=context)
    v1 = client.CoreV1Api()

    nodes = v1.list_node().items
    pods  = v1.list_pod_for_all_namespaces().items

    node_ready = all(
        any(c.type == "Ready" and c.status == "True" for c in n.status.conditions)
        for n in nodes
    )

    cloud_pods   = [p for p in pods if cloud in (p.metadata.namespace or "")]
    running_pods = [p for p in cloud_pods if p.status.phase == "Running"]

    return {
        "cloud":        cloud,
        "nodes":        len(nodes),
        "node_ready":   node_ready,
        "pods_total":   len(cloud_pods),
        "pods_running": len(running_pods),
        "healthy":      node_ready and len(running_pods) == len(cloud_pods),
    }

def main():
    table = Table(title=f"Multi-Cloud Health — {datetime.datetime.now().strftime('%H:%M:%S')}")
    table.add_column("Cloud",        style="cyan")
    table.add_column("Nodes",        style="white")
    table.add_column("Node Ready",   style="white")
    table.add_column("Pods Running", style="white")
    table.add_column("Status",       style="white")

    for cloud, context in CLOUDS.items():
        try:
            h = check_health(cloud, context)
            status = "[green]✓ HEALTHY[/green]" if h["healthy"] else "[red]✗ DEGRADED[/red]"
            table.add_row(
                cloud,
                str(h["nodes"]),
                "✓" if h["node_ready"] else "✗",
                f"{h['pods_running']}/{h['pods_total']}",
                status,
            )
        except Exception as e:
            table.add_row(cloud, "-", "-", "-", f"[red]ERROR: {e}[/red]")

    console.print(table)

if __name__ == "__main__":
    main()
