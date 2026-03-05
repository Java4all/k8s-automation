# Kubernetes Cluster Automation with Ansible & GitLab CI/CD

Complete automation solution for deploying a production-grade Kubernetes cluster on Ubuntu 24.04.3 LTS using Ansible playbooks and GitLab CI/CD pipeline.

## 📋 Features

- **Three Master Nodes** - High availability control plane with load balancer (F5 VIP)
- **Three Worker Nodes** - Scalable compute capacity
- **Containerized Runtime** - Docker + Containerd with systemd cgroup support
- **Kubernetes 1.34** - Latest stable version support
- **Calico CNI** - Enterprise-grade network plugin
- **Proxy Support** - Built-in proxy configuration for enterprise networks
- **Automated Deployment** - Full GitLab CI/CD pipeline integration
- **Health Checks** - Comprehensive verification and monitoring
- **Configuration as Code** - YAML-driven cluster configuration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              GitLab Repository                               │
│  ┌──────────────┐      ┌────────────────────────────────┐  │
│  │ Config YAML  │      │    Ansible Playbooks & Roles   │  │
│  └──────────────┘      └────────────────────────────────┘  │
│         ▼                              ▼                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         GitLab CI/CD Pipeline (.gitlab-ci.yml)      │   │
│  │  - Validate config & SSH connectivity               │   │
│  │  - Generate inventory dynamically                   │   │
│  │  - Execute Ansible playbooks                        │   │
│  │  - Verify cluster health                            │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬──────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          Target Infrastructure                               │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │      Kubernetes Control Plane (HA)                  │   │
│  │  Master1 (10.0.32.10) │ Master2 (10.0.32.11)│M3   │   │
│  │  ◄──────────────────────────────────────────────►  │   │
│  │          F5 VIP: 172.23.60.153:6443                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │    Kubernetes Worker Nodes                          │   │
│  │  Worker1 (10.0.32.2) │ Worker2 (10.0.32.3) │W3    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │    Network Plugin: Calico (v3.31.3)                 │   │
│  │    Pod CIDR: 10.0.68.0/21                           │   │
│  │    Service CIDR: 10.0.76.0/22                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
k8s-ansible-automation/
├── config/
│   └── cluster-config.example.yaml      # Configuration template
├── playbooks/
│   └── deploy-k8s-cluster.yml           # Main orchestration playbook
├── roles/
│   ├── common/                          # Network, NTP, prerequisites
│   ├── docker/                          # Docker installation & config
│   ├── containerd/                      # Containerd runtime setup
│   ├── kubernetes/                      # K8s packages & system config
│   ├── master/                          # Control plane initialization
│   ├── worker/                          # Worker node joining
│   ├── calico/                          # CNI plugin deployment
│   └── verification/                    # Health checks & verification
├── inventories/
│   ├── inventory.py                     # Dynamic inventory generator
│   └── hosts.ini                        # Static inventory template
├── gitlab-ci/
│   └── .gitlab-ci.yml                   # CI/CD pipeline definition
├── docs/
│   ├── README.md                        # This file
│   ├── QUICKSTART.md                    # Quick start guide
│   ├── CONFIGURATION.md                 # Detailed configuration guide
│   ├── DEPLOYMENT.md                    # Deployment procedures
│   └── TROUBLESHOOTING.md              # Troubleshooting guide
└── .gitignore
```

## 🚀 Quick Start

### Prerequisites

- GitLab instance with CI/CD enabled
- Ubuntu 24.04.3 LTS VMs already created with:
  - 3 Master nodes (vmm1, vmm2, vmm3)
  - 3 Worker nodes (vmw1, vmw2, vmw3)
  - Network connectivity between all nodes
  - SSH access from GitLab runner to all nodes
- F5 load balancer configured with VIP (172.23.60.153:6443)
- Network connectivity to Kubernetes and Calico repositories

### 1. Clone Repository

```bash
git clone <your-gitlab-repo>
cd k8s-ansible-automation
```

### 2. Configure Cluster

Copy and customize the configuration file:

```bash
cp config/cluster-config.example.yaml config/cluster-config.yaml
# Edit cluster-config.yaml with your environment details
```

Key configuration points:
- Update node IPs and hostnames
- Set control plane VIP endpoint
- Configure pod and service CIDRs
- Set proxy settings (if required)
- Adjust Kubernetes version if needed

### 3. Setup GitLab CI/CD Variables

In GitLab project settings, add these CI/CD variables:

```
SSH_PRIVATE_KEY          # Private key for SSH access (protected, masked)
CONFIG_FILE              # Path to config file (default: config/cluster-config.yaml)
```

### 4. Trigger Deployment

Option A: Push to repository (triggers pipeline automatically)
```bash
git add .
git commit -m "Deploy kubernetes cluster"
git push origin main
```

Option B: Manual trigger in GitLab
- Go to CI/CD > Pipelines
- Click "Run Pipeline"
- Set CONFIG_FILE variable if different from default

### 5. Monitor Deployment

Watch pipeline progress in GitLab:
- Validate stage: Configuration and connectivity checks
- Prepare stage: Inventory generation and variable setup
- Deploy stage: Ansible playbook execution
- Verify stage: Cluster health checks
- Cleanup stage: Resource cleanup

Expected duration: 30-60 minutes

## 📝 Configuration

### Minimal Configuration Example

```yaml
cluster:
  name: "production-k8s"
  k8s_version: "1.34"
  control_plane:
    endpoint_vip: "172.23.60.153"
    endpoint_port: 6443
  networking:
    pod_cidr: "10.0.68.0/21"
  proxy:
    enabled: true
    http_proxy: "http://proxy.company.com:8080"

nodes:
  masters:
    - name: "vmm1"
      ip: "10.0.32.10"
  workers:
    - name: "vmw1"
      ip: "10.0.32.2"
```

See `CONFIGURATION.md` for complete reference.

## 🔄 Deployment Process

1. **Validation Phase**
   - Check configuration YAML syntax
   - Verify SSH connectivity to all nodes
   - Validate deployment prerequisites

2. **Preparation Phase**
   - Generate dynamic inventory
   - Export deployment variables
   - Prepare environment

3. **Deployment Phase**
   - Install prerequisites and configure network (common role)
   - Install Docker and Containerd (docker/containerd roles)
   - Install Kubernetes packages (kubernetes role)
   - **System Reboot** (apply kernel changes)
   - Initialize first master node (master role)
   - Deploy Calico CNI (calico role)
   - Join additional master nodes (master role)
   - Join worker nodes in parallel (worker role)

4. **Verification Phase**
   - Verify cluster connectivity
   - Check node status
   - Validate pod status
   - Generate deployment report

## 📊 What Gets Deployed

### System Configuration
- Ubuntu 24.04.3 LTS kernel with required modules
- Network prerequisites (DNS, NTP)
- Disabled: swap, nftables, apparmor
- Kernel parameters: IP forwarding, bridge filtering
- Timezone, hostname configuration

### Container Runtime
- **Docker.io** - Latest stable from Ubuntu repos
- **Containerd** - Latest stable with systemd cgroup
- Proxy configuration for both runtimes
- Environment variables for proxy support

### Kubernetes Stack
- **Kubelet** - Node agent
- **Kubeadm** - Cluster initialization tool
- **Kubectl** - CLI tool
- **Version**: 1.34 (configurable)

### Cluster Architecture
- **3 Master Nodes**: etcd, kube-apiserver, kube-controller-manager, kube-scheduler
- **3 Worker Nodes**: kubelet, kube-proxy, container runtime
- **Load Balancer**: F5 VIP for HA control plane access
- **CNI**: Calico v3.31.3

### Network Configuration
- **Pod Network CIDR**: 10.0.68.0/21
- **Service CIDR**: 10.0.76.0/22
- **DNS Servers**: 8.8.8.8, 8.8.4.4
- **NTP Servers**: Ubuntu NTP pools

## 🛠️ Troubleshooting

See `TROUBLESHOOTING.md` for:
- Common deployment issues
- Network connectivity problems
- Kubernetes cluster debugging
- Log collection and analysis
- Recovery procedures

## 📚 Documentation

- **QUICKSTART.md** - Step-by-step deployment walkthrough
- **CONFIGURATION.md** - Complete configuration reference
- **DEPLOYMENT.md** - Detailed deployment procedures
- **TROUBLESHOOTING.md** - Issues and solutions

## 🔒 Security Considerations

- SSH keys stored as masked variables in GitLab
- Kubeadm certificate rotation configured
- RBAC enabled by default
- Network policies supported via Calico
- TLS for API server communication
- No hardcoded credentials in code

## 📈 Scaling & Maintenance

### Add Worker Nodes

1. Add node definition to `cluster-config.yaml`
2. Update inventory
3. Run worker deployment playbook
4. Verify node status

### Upgrade Kubernetes

1. Update `k8s_version` in config
2. Rerun deployment pipeline
3. Monitor for issues

### Monitoring & Observability

Deploy monitoring stack separately:
- Prometheus for metrics
- Grafana for visualization
- ELK for logging
- Calico Network Policies

## 🤝 Support & Contribution

For issues, improvements, or questions:
1. Check `TROUBLESHOOTING.md`
2. Review pipeline logs in GitLab
3. Check system logs on nodes
4. Contact infrastructure team

## 📄 License

Internal use only

## 📞 Contact

Infrastructure team: infrastructure@company.com
