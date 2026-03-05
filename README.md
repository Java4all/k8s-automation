# Kubernetes Cluster Automation with Ansible & GitLab CI/CD

Automation for deploying Kubernetes cluster using Ansible playbooks and GitLab CI/CD pipeline.

##Quick Start

### Prerequisites

- GitLab instance with CI/CD enabled
- Ubuntu 24.04.3 LTS VMs already created:
  - 3 Master nodes (for example vmm1, vmm2, vmm3)
  - 3 Worker nodes (for example vmw1, vmw2, vmw3)
  - Network connectivity between all nodes
  - SSH access from GitLab runner to all nodes
- F5 load balancer configured with VIP (IPaddress:Port)

### 1. Clone Repository

```bash
git clone <your-gitlab-repo>
cd k8s-automation
```

### 2. Configure

Edit and customize the configuration file:

```bash
cp config/cluster-config.example.yaml config/cluster-config.yaml
# Edit cluster-config.yaml with your environment details
```

Key configurations:
- Update node IPs and hostnames
- Set control plane VIP endpoint
- Configure pod and service CIDRs
- Set proxy settings (if required)
- Adjust Kubernetes version if needed

### 3. Setup CI/CD Variables

In GitLab project settings, add these CI/CD variables:

```
SSH_PRIVATE_KEY          # Private key for SSH access (protected, masked)
CONFIG_FILE              # Path to config file (default: config/cluster-config.yaml)
```

### 4. Trigger Deployment

Manual trigger in GitLab UI:
- Go to CI/CD > Pipelines
- Click "Run Pipeline"
- Set CONFIG_FILE variable if different from default


## Configuration details

### Minimal Configuration Example

```yaml
cluster:
  name: "prod-k8s"
  k8s_version: "1.34"
  control_plane:
    endpoint_vip: "172.20.10.199"
    endpoint_port: 6443
  networking:
    pod_cidr: "10.0.32.0/21"
  proxy:
    enabled: true
    http_proxy: "http://example.proxy:8080"
    https_proxy: "http://example.proxy:8080"
    no_proxy: ""

nodes:
  masters:
    - name: "vmm1"
      ip: "10.0.32.10"
  workers:
    - name: "vmw1"
      ip: "10.0.32.2"
```
