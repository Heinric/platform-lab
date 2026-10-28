# platform-lab

[![CI](https://github.com/Heinric/platform-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Heinric/platform-lab/actions/workflows/ci.yml)

A local lab for practicing multi-cloud platform engineering without a cloud bill. It simulates three
environments (AWS, Azure, and GCP) as three local Kubernetes clusters, provisions them with
**Terraform**, deploys the same app to all three with **Helm** using per-cloud values, and checks
their state with **Python** automation.

```
                       ┌──────────────── kind clusters ────────────────┐
 terraform/<cloud>  ──▶│  kind-aws        kind-azure        kind-gcp    │
 (namespace per cloud) │  aws-dev ns      azure-dev ns      gcp-dev ns  │
                       │  3 replicas      2 replicas        2 replicas  │
 helm/app + values ───▶│                                                │
                       └────────────────────────────────────────────────┘
                                          ▲
 python/automation ───────────────────────┘  inventory + health report
```

## What's inside

| Path | What it does |
|---|---|
| `terraform/modules/kubernetes` | Reusable module that creates a `<cloud>-<env>` namespace with standard labels |
| `terraform/{aws,azure,gcp}` | One root module per cloud, each pointing at its own kube context and local state |
| `helm/app` | Chart for the app, with `values-<cloud>.yaml` overriding replicas and labels per cloud |
| `python/automation/inventory.py` | Lists namespaces, pods, and deployments per cloud |
| `python/automation/health.py` | Checks node readiness and running pods, reporting each cloud as healthy or degraded |
| `scripts/` | Environment check, cluster creation, and context switching |
| `.github/workflows/ci.yml` | Ruff + pytest, `terraform fmt`/`validate` for each cloud, and `helm lint` |

## Prerequisites

Docker, [kind](https://kind.sigs.k8s.io/), kubectl, Terraform ≥ 1.0, Helm 3, and Python 3.10+.
The scripts are Bash, so on Windows use WSL or Git Bash.

```bash
./scripts/check-env.sh
```

## Running it

**1. Create the three clusters**

```bash
./scripts/create-clusters.sh      # kind-aws, kind-azure, kind-gcp
```

**2. Provision the namespaces with Terraform**

```bash
for cloud in aws azure gcp; do
  terraform -chdir=terraform/$cloud init
  terraform -chdir=terraform/$cloud apply -auto-approve
done
```

**3. Deploy the app to each cloud with Helm**

```bash
for cloud in aws azure gcp; do
  helm upgrade --install platform-app helm/app \
    -f helm/app/values-$cloud.yaml --kube-context kind-$cloud
done
```

**4. Check the result**

```bash
cd python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python automation/inventory.py
python automation/health.py
```

`health.py` prints one row per cloud with nodes, ready status, running pods, and `HEALTHY` or `DEGRADED`.
To switch kubectl between clusters, use `./scripts/use-cloud.sh aws|azure|gcp`.

**Clean up**

```bash
kind delete clusters aws azure gcp
```

## Tests

The automation is tested with mocked Kubernetes clients, so no cluster is needed:

```bash
cd python
pip install -r requirements-dev.txt
ruff check .
pytest
```

## Design notes

- **One module, three roots.** Each cloud has its own root module and state file, so a change to one
  environment can't touch the others, while the namespace logic lives in a single shared module.
- **Per-cloud values instead of per-cloud charts.** The chart is the same everywhere; only the
  differences (replicas, labels) live in `values-<cloud>.yaml`.
- **Local state on purpose.** State is kept in `.tfstate/` (git-ignored) to keep the lab self-contained.
  In a real setup each environment would use a remote backend with locking (S3 + DynamoDB, Azure
  Storage, or GCS).

## Next steps

- Swap the kind clusters for real EKS, AKS, and GKE modules behind the same interface
- Remote state with locking per environment
- Replace the nginx placeholder with a real service and add readiness and liveness probes
