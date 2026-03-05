# Quick Start Guide

## 5-Minute Setup

### Step 1: Clone and Setup (2 minutes)

```bash
# Clone the repository
git clone <your-gitlab-url>/k8s-ansible-automation.git
cd k8s-ansible-automation

# Copy configuration template
cp config/cluster-config.example.yaml config/cluster-config.yaml

# Update with your environment
nano config/cluster-config.yaml
```

### Step 2: Configure Nodes in YAML

Edit `config/cluster-config.yaml` and update:

```yaml
nodes:
  masters:
    - name: "vmm1"
      ip: "10.0.32.10"
    - name: "vmm2"
      ip: "10.0.32.11"
    - name: "vmm3"
      ip: "10.0.32.12"
  workers:
    - name: "vmw1"
      ip: "10.0.32.2"
    - name: "vmw2"
      ip: "10.0.32.3"
    - name: "vmw3"
      ip: "10.0.32.4"
```

Key updates:
- **Control Plane VIP**: `cluster.control_plane.endpoint_vip` → Your F5 VIP
- **Pod Network**: `cluster.networking.pod_cidr` → Your pod CIDR
- **Proxy**: `cluster.proxy.http_proxy` → Your proxy (if needed)
- **DNS/NTP**: Update servers if different

### Step 3: Add GitLab CI/CD Variables (2 minutes)

1. Go to **GitLab Project → Settings → CI/CD → Variables**

2. Add two variables:

   | Variable | Value | Protected | Masked |
   |----------|-------|-----------|--------|
   | `SSH_PRIVATE_KEY` | Your SSH private key | ✓ | ✓ |
   | `CONFIG_FILE` | `config/cluster-config.yaml` | ✗ | ✗ |

3. Save variables

### Step 4: Trigger Deployment (1 minute)

#### Option A: Automatic (Git Push)
```bash
git add .
git commit -m "Deploy kubernetes cluster"
git push origin main
```
Pipeline starts automatically → Check GitLab CI/CD tab

#### Option B: Manual Trigger
1. Go to **GitLab Project → CI/CD → Pipelines**
2. Click **Run Pipeline**
3. (Optional) Override CONFIG_FILE if needed
4. Click **Run Pipeline**

### Step 5: Monitor Progress

1. Go to **CI/CD → Pipelines**
2. Click the pipeline ID to view stages:
   - `validate` - Checks configuration (2 min)
   - `prepare` - Generates inventory (1 min)
   - `deploy` - Runs Ansible playbooks (45-60 min)
   - `verify` - Health checks (5 min)
   - `cleanup` - Cleanup (1 min)

3. Watch the **deploy:kubernetes** job logs

## Detailed Workflow

### Configuration File Structure

```yaml
cluster:
  name: "my-k8s-cluster"           # Cluster identifier
  environment: "prod"               # dev/staging/prod
  k8s_version: "1.34"              # Kubernetes version
  
  control_plane:
    endpoint_vip: "172.23.60.153"  # F5 VIP for HA
    endpoint_port: 6443             # API server port
  
  networking:
    pod_cidr: "10.0.68.0/21"       # Pod network range
    service_cidr: "10.0.76.0/22"   # Service network range
    dns_servers:
      - "8.8.8.8"
    ntp_servers:
      - "0.ubuntu.pool.ntp.org"
  
  proxy:
    enabled: true
    http_proxy: "http://proxy:8080"
    https_proxy: "http://proxy:8080"
    no_proxy_list:
      - "localhost"
      - "127.0.0.1"
      - "10.0.0.0/8"
```

### Node Configuration

```yaml
nodes:
  masters:
    - name: "vmm1"
      hostname: "vmm1"
      ip: "10.0.32.10"
      netmask: "255.255.240.0"    # /20
      gateway: "10.0.32.1"
      role: "master"
```

### Validation Checklist

Before deployment, verify:

- [ ] All VMs are running and have network connectivity
- [ ] SSH access configured to all nodes
- [ ] DNS names resolve correctly
- [ ] F5 VIP is configured and listening on port 6443
- [ ] Proxy is accessible from nodes (if enabled)
- [ ] Configuration YAML is valid (run: `python3 -c "import yaml; yaml.safe_load(open('config/cluster-config.yaml'))"`)
- [ ] GitLab CI/CD variables are set
- [ ] Runner has network access to all nodes

## Common Configuration Scenarios

### Scenario 1: Basic Setup (No Proxy)

```yaml
cluster:
  proxy:
    enabled: false

nodes:
  masters:
    - name: "vmm1"
      ip: "10.0.32.10"
```

### Scenario 2: Corporate Network with Proxy

```yaml
cluster:
  proxy:
    enabled: true
    http_proxy: "http://corp-proxy.company.com:8080"
    https_proxy: "http://corp-proxy.company.com:8080"
    no_proxy_list:
      - "localhost"
      - "10.0.0.0/8"
      - "company.local"
```

### Scenario 3: Different Pod Network

```yaml
cluster:
  networking:
    pod_cidr: "192.168.0.0/16"      # Different range
    service_cidr: "10.96.0.0/16"
```

## Deployment Output

### During Deployment

Watch logs for progress:
```
...
deploy:kubernetes
├── Setup prerequisites (common role)
├── Install Docker & Containerd
├── Install Kubernetes packages
├── Reboot nodes
├── Initialize Master 1
├── Deploy Calico CNI
├── Join Masters 2 & 3
├── Join Workers 1-3
└── Health verification
...
```

### After Successful Deployment

Expected output:
```
KUBERNETES CLUSTER DEPLOYMENT COMPLETE
==========================================
✓ All 6 nodes joined successfully
✓ Calico networking deployed
✓ All pods are running
✓ Cluster is ready for use
```

## Post-Deployment Access

### Access Kubernetes Cluster

1. Copy kubeconfig from first master:
```bash
scp ubuntu@10.0.32.10:~/.kube/config ~/.kube/config
chmod 600 ~/.kube/config
```

2. Verify cluster access:
```bash
kubectl get nodes
kubectl get pods --all-namespaces
```

### Verify Cluster Health

```bash
# Check nodes
kubectl get nodes -o wide

# Check system pods
kubectl get pods -n calico-system
kubectl get pods -n kube-system

# Check services
kubectl get svc --all-namespaces

# Check cluster info
kubectl cluster-info
```

## Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| SSH connection fails | Check SSH_PRIVATE_KEY variable, verify network connectivity |
| Ansible playbook fails | Check node logs in `/var/log/ansible/`, verify prerequisites |
| Kubernetes API not responding | Wait for master initialization, check control plane logs |
| Calico pods not running | Check pod logs: `kubectl logs -n calico-system -l k8s-app=calico-node` |
| Worker nodes not joining | Verify join command, check kubelet logs: `systemctl status kubelet` |

See `TROUBLESHOOTING.md` for detailed diagnostics.

## Rolling Back

If deployment fails:

1. **Stop pipeline** - Click "Cancel" in GitLab
2. **Investigate logs** - Check pipeline job logs
3. **Fix configuration** - Update `config/cluster-config.yaml`
4. **Retry** - Push changes to trigger new pipeline

To completely reset nodes (if needed):
```bash
# On each node:
kubeadm reset --force
rm -rf /etc/kubernetes
rm -rf /var/lib/etcd
```

## Next Steps

1. Deploy monitoring (Prometheus + Grafana)
2. Configure persistent storage (if needed)
3. Set up container image registry
4. Configure ingress controller
5. Deploy applications

See project documentation for detailed guides.
