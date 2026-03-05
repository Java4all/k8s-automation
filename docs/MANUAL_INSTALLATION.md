# Manual Kubernetes Cluster Deployment - Complete Guide

Complete guide for manually running Ansible playbooks to deploy Kubernetes cluster.
Use this for testing, troubleshooting, or local development before GitLab CI/CD deployment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Testing & Verification](#testing--verification)
5. [Advanced Manual Options](#advanced-manual-options)
6. [Troubleshooting](#troubleshooting)
7. [Common Tasks](#common-tasks)

---

## Prerequisites

### On Your Local Machine (Where You Run Ansible)

**OS Requirements:**
- Linux, macOS, or Windows with WSL
- SSH client installed
- Python 3.10+

**Install Required Packages:**

```bash
# For Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    ansible \
    python3 \
    python3-pip \
    git

# Install Python dependencies
pip3 install pyyaml jinja2 netaddr

# Verify installations
ansible --version
python3 --version
```

**SSH Configuration:**

```bash
# Generate SSH key (if not already done)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Add public key to all cluster nodes
for node in 10.0.32.10 10.0.32.11 10.0.32.12 10.0.32.2 10.0.32.3 10.0.32.4; do
  ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@$node
done

# Test SSH access
ssh ubuntu@10.0.32.10 "hostname"
# Should output: vmm1
```

### Target Cluster Nodes

**OS Requirements:**
- All 6 nodes: Ubuntu 24.04.3 LTS
- Network connectivity between nodes
- SSH access from your machine to all nodes
- Internet access (or proxy configured)

---

## Quick Start

### 1. Extract Archive

```bash
tar -xzf k8s-automation-complete.tar.gz
cd k8s-ansible-automation
```

### 2. Configure Cluster

```bash
# Copy configuration template
cp config/cluster-config.example.yaml config/cluster-config.yaml

# Edit with your environment
nano config/cluster-config.yaml

# Key fields to update:
# - cluster.control_plane.endpoint_vip: Your F5 VIP (172.23.60.153)
# - cluster.networking.pod_cidr: Pod network (10.0.68.0/21)
# - nodes.masters: Master node IPs (vmm1-3)
# - nodes.workers: Worker node IPs (vmw1-3)
# - cluster.proxy: Proxy settings (if needed)
```

### 3. Generate Inventory

```bash
python3 inventories/inventory.py --config config/cluster-config.yaml > inventory.json
```

### 4. Test Connectivity

```bash
ansible -i inventory.json all -m ping

# Expected output:
# vmm1 | SUCCESS => {
#     "changed": false,
#     "ping": "pong"
# }
# ... (similar for all 6 nodes)
```

### 5. Run Playbook

```bash
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  -v

# -v: verbose output
# Add more -v for increased verbosity: -vv, -vvv, -vvvv
```

---

## Step-by-Step Setup

### Step 1: Extract Archive

```bash
tar -xzf k8s-automation-complete.tar.gz
cd k8s-ansible-automation

# Verify directory structure
ls -la
# Should show: playbooks/, roles/, config/, inventories/, docs/, etc.
```

### Step 2: Review Configuration Template

```bash
cat config/cluster-config.example.yaml

# Key sections:
# - cluster: cluster name, k8s version, control plane endpoint, networking, proxy
# - nodes: master and worker node definitions
# - container_runtime: docker and containerd settings
# - deployment: timeouts and parallel settings
```

### Step 3: Create Your Configuration

```bash
cp config/cluster-config.example.yaml config/cluster-config.yaml
nano config/cluster-config.yaml

# Example configuration:
cat << 'EOF' > config/cluster-config.yaml
cluster:
  name: "production-k8s"
  environment: "prod"
  k8s_version: "1.34"
  
  control_plane:
    endpoint_vip: "172.23.60.153"
    endpoint_port: 6443
  
  networking:
    pod_cidr: "10.0.68.0/21"
    service_cidr: "10.0.76.0/22"
    dns_servers:
      - "8.8.8.8"
      - "8.8.4.4"
  
  proxy:
    enabled: true
    http_proxy: "http://proxy.company.com:8080"
    https_proxy: "http://proxy.company.com:8080"
    no_proxy_list:
      - "localhost"
      - "127.0.0.1"
      - "10.0.0.0/8"

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

deployment:
  skip_verification: false
  parallel_workers: 3
EOF
```

### Step 4: Validate Configuration

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config/cluster-config.yaml')); print('✓ Configuration valid')"

# Expected output: ✓ Configuration valid
```

### Step 5: Generate Inventory

```bash
# Generate dynamic inventory from configuration
python3 inventories/inventory.py --config config/cluster-config.yaml > inventory.json

# Verify inventory was created
ls -la inventory.json
wc -l inventory.json
```

### Step 6: View Generated Inventory

```bash
# Pretty print the inventory
python3 inventories/inventory.py --config config/cluster-config.yaml | python3 -m json.tool

# You should see:
# - all: group containing all nodes
# - masters: group with 3 master nodes
# - workers: group with 3 worker nodes
# - _meta: metadata for each node
```

### Step 7: Test SSH Connectivity

```bash
# Test all nodes
for ip in 10.0.32.10 10.0.32.11 10.0.32.12 10.0.32.2 10.0.32.3 10.0.32.4; do
  echo "Testing $ip..."
  ssh -o ConnectTimeout=5 ubuntu@$ip "hostname && uname -a" || echo "FAILED: $ip"
done
```

### Step 8: Test Ansible Connectivity

```bash
# Ping all nodes via Ansible
ansible -i inventory.json all -m ping

# Expected output for each node:
# vmm1 | SUCCESS => {
#     "changed": false,
#     "ping": "pong"
# }
```

### Step 9: Run Playbook

```bash
# Full verbose run
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  -v

# Expected duration: 60-75 minutes
```

---

## Testing & Verification

### Pre-Deployment Checks

#### 1. Validate All Node IPs

```bash
python3 inventories/inventory.py --config config/cluster-config.yaml | python3 -m json.tool | grep ansible_host
```

#### 2. Check Ansible Configuration

```bash
# View ansible settings
cat ansible.cfg

# Test with verbose output
ansible --version
```

#### 3. Verify SSH Keys

```bash
# List SSH keys
ssh-add -l

# Add key to SSH agent if needed
ssh-add ~/.ssh/id_rsa
```

### Dry Run (Check Mode - No Changes)

**Test the playbook without making any changes:**

```bash
# Full playbook dry run
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --check \
  -v

# What to expect:
# - Shows all tasks that WOULD be executed
# - Marked with "changed" indicators
# - No actual changes made to nodes
```

### View Playbook Structure

```bash
# List all tasks
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --list-tasks

# List all roles
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --list-roles

# List all tags
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --list-tags
```

---

## Advanced Manual Options

### Run Specific Role Only

**Test individual roles before full deployment:**

```bash
# Common role (network, DNS, NTP, prerequisites)
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --tags common \
  -v

# Docker role
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --tags docker \
  -v

# Containerd role
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --tags containerd \
  -v

# Kubernetes packages
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --tags kubernetes \
  -v

# Master initialization
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --tags "master,init" \
  -v

# Worker deployment
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --tags "worker" \
  -v

# Calico CNI
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --tags "calico,cni" \
  -v

# Verification only
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --tags "verification,health-check" \
  -v
```

### Run Specific Host Group

**Test on subset of nodes:**

```bash
# Run only on masters
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --limit masters \
  -v

# Run only on workers
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --limit workers \
  -v

# Run on specific node
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --limit vmm1 \
  -v
```

### Step-Through Playbook (Interactive)

**Pause at each task for confirmation:**

```bash
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --step \
  -v

# Prompts:
# (y)es, (n)o, (c)ontinue, (r)edact, (d)ebug, (v)erbosity level or /regex/: 
# - y: execute this task
# - n: skip this task
# - c: continue without stepping
# - d: open debugger
```

### Enable Maximum Verbosity

```bash
# Standard run with different verbosity levels

# -v: verbose (show output of each task)
ansible-playbook ... -v

# -vv: more verbose (show internal variables)
ansible-playbook ... -vv

# -vvv: even more verbose (show connections)
ansible-playbook ... -vvv

# -vvvv: debug mode (extreme verbosity)
ansible-playbook ... -vvvv
```

### Skip Tasks

**Skip certain tasks during execution:**

```bash
# Skip reboot task (useful for testing)
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --skip-tags reboot \
  -v

# Skip verification
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --skip-tags verification \
  -v
```

### Run with Custom Variables

**Override configuration variables:**

```bash
# Set k8s version from command line
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  --extra-vars 'cluster.k8s_version=1.35' \
  playbooks/deploy-k8s-cluster.yml \
  -v

# Disable proxy for this run
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  --extra-vars 'cluster.proxy.enabled=false' \
  playbooks/deploy-k8s-cluster.yml \
  -v
```

---

## Troubleshooting

### SSH Connection Issues

**Problem: "Permission denied (publickey)"**

```bash
# 1. Verify SSH key exists
ls -la ~/.ssh/id_rsa

# 2. Check SSH key permissions
chmod 600 ~/.ssh/id_rsa

# 3. Test SSH manually
ssh -v ubuntu@10.0.32.10 "echo SSH works"

# 4. Check if key is in authorized_keys on node
ssh ubuntu@10.0.32.10 "grep $(cat ~/.ssh/id_rsa.pub) ~/.ssh/authorized_keys"

# 5. Add key to SSH agent
ssh-add ~/.ssh/id_rsa

# 6. Check agent is working
ssh-add -l
```

### Inventory Generation Issues

**Problem: "No Python found"**

```bash
# Check Python version
python3 --version

# Verify it's 3.10+
python3 -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10+ required'"

# Install if needed
sudo apt-get install python3
```

**Problem: Inventory generation fails**

```bash
# 1. Validate YAML syntax first
python3 -c "import yaml; yaml.safe_load(open('config/cluster-config.yaml')); print('Valid')"

# 2. Check if pyyaml is installed
pip3 install pyyaml

# 3. Run inventory script with debug
python3 inventories/inventory.py --config config/cluster-config.yaml 2>&1 | head -50

# 4. Check for YAML formatting issues
cat config/cluster-config.yaml | grep -E "^\s+-" | head -5
```

### Playbook Execution Issues

**Problem: "No hosts matched"**

```bash
# 1. Verify inventory was generated
cat inventory.json | python3 -m json.tool | grep '"masters"'

# 2. Check if hosts are in inventory
python3 inventories/inventory.py --config config/cluster-config.yaml | python3 -m json.tool | grep '"vmm1"'

# 3. Regenerate inventory
python3 inventories/inventory.py --config config/cluster-config.yaml > inventory.json

# 4. Test with ansible
ansible -i inventory.json all -m ping
```

**Problem: "Timeout waiting for connection"**

```bash
# 1. Check network connectivity
ping -c 3 10.0.32.10

# 2. Check if nodes are up
for ip in 10.0.32.{10..12} 10.0.32.{2..4}; do
  ping -c 1 -W 1 $ip && echo "$ip: UP" || echo "$ip: DOWN"
done

# 3. Check SSH explicitly
ssh -o ConnectTimeout=5 ubuntu@10.0.32.10 "date"

# 4. Check firewall
ssh ubuntu@10.0.32.10 "sudo ufw status"

# 5. Check if SSH service is running
ssh ubuntu@10.0.32.10 "sudo systemctl status ssh"
```

### Task Failures

**Problem: "Task failed - FATAL UNRECOVERABLE ERROR"**

```bash
# 1. Check task output in detail
# Increase verbosity: -vvv or -vvvv

# 2. Check node logs
ssh ubuntu@10.0.32.10 "journalctl -xe"

# 3. Check specific service status
ssh ubuntu@10.0.32.10 "sudo systemctl status docker"

# 4. Check disk space
ssh ubuntu@10.0.32.10 "df -h /"

# 5. Check memory
ssh ubuntu@10.0.32.10 "free -h"
```

### Rerun Failed Tasks

**Resume from where it failed:**

```bash
# Run with start-at-task to resume
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --start-at-task "Task name from error message" \
  -v

# Example: resume from docker installation
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --start-at-task "Install docker.io" \
  -v
```

---

## Common Tasks

### View All Available Hosts

```bash
ansible -i inventory.json all --list-hosts

# Output:
# vmm1
# vmm2
# vmm3
# vmw1
# vmw2
# vmw3
```

### Gather Facts from Nodes

```bash
# Get system information from all nodes
ansible -i inventory.json all -m setup

# Get specific facts
ansible -i inventory.json all -m setup -a "filter=ansible_os_family"
ansible -i inventory.json all -m setup -a "filter=ansible_processor"
ansible -i inventory.json all -m setup -a "filter=ansible_memtotal_mb"
```

### Run Arbitrary Commands on Nodes

```bash
# Run command on all nodes
ansible -i inventory.json all -m shell -a "hostname"

# Run on specific node
ansible -i inventory.json vmm1 -m shell -a "hostname"

# Run on masters only
ansible -i inventory.json masters -m shell -a "cat /etc/os-release"

# Run on workers only
ansible -i inventory.json workers -m shell -a "df -h /"
```

### Check Playbook Syntax

```bash
# Validate playbook syntax
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --syntax-check

# Output: "Playbook syntax is OK"
```

### View Playbook Variables

```bash
# Show all variables that will be used
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --extra-vars '{"debug": true}' \
  -v | grep "VARIABLE" | head -20
```

### Monitor Running Playbook

```bash
# In another terminal while playbook is running
watch -n 5 "ssh ubuntu@10.0.32.10 'ps aux | grep ansible'"

# Or check system load
watch -n 5 "ssh ubuntu@10.0.32.10 'top -b -n 1 | head -20'"

# Or monitor logs
ssh ubuntu@10.0.32.10 "tail -f /var/log/syslog" &
ssh ubuntu@10.0.32.10 "journalctl -f" &
```

### Collect Deployment Logs

```bash
# Save playbook output to file
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  -v 2>&1 | tee deployment.log

# Later analyze logs
grep "FAILED\|ERROR" deployment.log
grep "CHANGED" deployment.log
wc -l deployment.log
```

### Reset and Redeploy Specific Node

```bash
# SSH to node and reset
ssh ubuntu@10.0.32.10 << 'EOF'
  sudo kubeadm reset --force 2>/dev/null
  sudo rm -rf /etc/kubernetes /var/lib/etcd
  sudo systemctl restart kubelet
  sudo systemctl restart docker
  sudo systemctl restart containerd
EOF

# Then rerun playbook (it's idempotent)
ansible-playbook \
  --inventory inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --limit vmm1 \
  -v
```

---

## Useful Ansible Commands Reference

```bash
# List all hosts
ansible -i inventory.json all --list-hosts

# List groups
ansible -i inventory.json localhost -m debug -a "msg={{ groups }}"

# Test connectivity
ansible -i inventory.json all -m ping

# Gather facts
ansible -i inventory.json all -m setup

# Run ad-hoc command
ansible -i inventory.json all -m shell -a "command here"

# Copy file to nodes
ansible -i inventory.json all -m copy -a "src=local dest=/remote/path"

# View playbook syntax
ansible-playbook ... --syntax-check

# List all tasks
ansible-playbook ... --list-tasks

# List all hosts in playbook
ansible-playbook ... --list-hosts

# Dry run (check mode)
ansible-playbook ... --check

# Step through (interactive)
ansible-playbook ... --step

# Start from specific task
ansible-playbook ... --start-at-task "Task name"

# Skip specific tags
ansible-playbook ... --skip-tags "tag1,tag2"

# Run specific tags
ansible-playbook ... --tags "tag1,tag2"

# Run on specific host
ansible-playbook ... --limit hostname

# Maximum verbosity
ansible-playbook ... -vvvv

# Save output to file
ansible-playbook ... 2>&1 | tee output.log
```

---

## Testing Workflow Summary

```bash
# 1. Extract and setup (5 min)
tar -xzf k8s-automation-complete.tar.gz
cd k8s-ansible-automation
cp config/cluster-config.example.yaml config/cluster-config.yaml
# Edit config with your IPs

# 2. Validate (2 min)
python3 -c "import yaml; yaml.safe_load(open('config/cluster-config.yaml')); print('✓')"
python3 inventories/inventory.py --config config/cluster-config.yaml > inventory.json

# 3. Test connectivity (1 min)
ansible -i inventory.json all -m ping

# 4. Dry run (5 min)
ansible-playbook -i inventory.json --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml --check -v

# 5. Run full playbook (60-75 min)
ansible-playbook -i inventory.json --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml -v

# 6. Verify deployment (10 min)
ssh ubuntu@10.0.32.10 "kubectl get nodes"
ssh ubuntu@10.0.32.10 "kubectl get pods --all-namespaces"
```

---

## Notes

- **Idempotent**: The playbook is safe to run multiple times. It won't break anything if re-run.
- **Interruption**: If playbook is interrupted, fix the issue and re-run from where it failed using `--start-at-task`.
- **Logs**: Check `/tmp/ansible.log` on nodes for detailed execution logs.
- **SSH**: Ensure SSH access is configured before running playbook.
- **Proxy**: If using corporate proxy, ensure `cluster.proxy` is configured correctly.

---

## For More Help

Refer to documentation in the archive:
- `docs/README.md` - Project overview
- `docs/QUICKSTART.md` - Quick setup guide
- `docs/CONFIGURATION.md` - Complete parameter reference
- `docs/TROUBLESHOOTING.md` - Detailed troubleshooting

Or check Ansible documentation:
- https://docs.ansible.com/
- https://docs.ansible.com/ansible/latest/index.html
