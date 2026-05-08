from kubernetes import client, config
from rich.table import Table
from rich.console import Console

CLOUDS = {
    "aws":   "kind-aws",
    "gcp":   "kind-gcp",
    "azure": "kind-azure",
}

console = Console()

def get_inventory(cloud: str, context: str) -> dict:
    config.load_kube_config(context=context)
    v1 = client.CoreV1Api()
    apps = client.AppsV1Api()

    namespaces = [n.metadata.name for n in v1.list_namespace().items
                  if cloud in n.metadata.name]

    pods = v1.list_pod_for_all_namespaces().items
    deployments = apps.list_deployment_for_all_namespaces().items

    cloud_pods = [p for p in pods if cloud in (p.metadata.namespace or "")]
    cloud_deps = [d for d in deployments if cloud in (d.metadata.namespace or "")]

    return {
        "cloud":       cloud,
        "namespaces":  namespaces,
        "pods":        len(cloud_pods),
        "deployments": len(cloud_deps),
    }

def main():
    table = Table(title="Multi-Cloud Inventory")
    table.add_column("Cloud",       style="cyan")
    table.add_column("Namespaces",  style="green")
    table.add_column("Pods",        style="yellow")
    table.add_column("Deployments", style="magenta")

    for cloud, context in CLOUDS.items():
        try:
            inv = get_inventory(cloud, context)
            table.add_row(
                inv["cloud"],
                ", ".join(inv["namespaces"]) or "-",
                str(inv["pods"]),
                str(inv["deployments"]),
            )
        except Exception as e:
            table.add_row(cloud, "ERROR", str(e), "-")

    console.print(table)

if __name__ == "__main__":
    main()
