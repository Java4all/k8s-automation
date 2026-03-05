# Troubleshooting Guide

## Pre-Deployment Issues

### SSH Connection Fails

**Error**: `Permission denied (publickey)`

**Causes & Solutions**:
1. SSH key not configured correctly
   ```bash
   # Verify SSH key format
   ssh-keygen -l -f ~/.ssh/id_rsa
   
   # Test SSH connection
   ssh -v ubuntu@10.0.32.10
   ```

2. SSH_PRIVATE_KEY variable not set
   ```bash
   # Check GitLab CI/CD variables
   # Settings → CI/CD → Variables
   # Ensure SSH_PRIVATE_KEY is set and not empty
   ```

3. Known hosts not updated
   ```bash
   # Run before pipeline:
   ssh-keyscan -t rsa 10.0.32.10 >> ~/.ssh/known_hosts
   ```

### Configuration File Not Found

**Error**: `ERROR: Config file config/cluster-config.yaml not found!`

**Solution**:
```bash
# Verify file exists
ls -la config/cluster-config.yaml

# Check GitLab CI/CD variable CONFIG_FILE
# Should match the actual file path in repository
```

### YAML Syntax Error

**Error**: `yaml.YAMLError: ...`

**Solution**:
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config/cluster-config.yaml'))"

# Check for common issues:
# - Tabs instead of spaces (YAML requires spaces)
# - Incorrect indentation
# - Missing colons
# - Unclosed quotes
```

### Invalid Network Configuration

**Error**: `Error validating CIDR ranges`

**Solution**:
```yaml
# Ensure valid CIDR notation
networking:
  pod_cidr: "10.0.68.0/21"        # ✓ Correct
  service_cidr: "10.0.76.0/22"    # ✓ Correct

# Not:
# pod_cidr: "10.0.68.0/21/24"     # ✗ Invalid
# pod_cidr: "10.0.68.0"           # ✗ Missing prefix
```

## Deployment Issues

### Common Ansible Errors

#### "Timeout waiting for reply"

**Cause**: Network connectivity issues

**Solution**:
```bash
# Verify node connectivity from runner
ansible all -m ping -i /tmp/inventory.json

# Check network routes
ip route show

# Check firewall rules
sudo iptables -L -n | grep 22
```

#### "Failed to validate API certificate"

**Cause**: System clock skew

**Solution**:
```bash
# On affected nodes:
timedatectl status           # Check time sync
ntpq -p                      # Check NTP status
sudo systemctl restart chrony # Restart NTP service
date                          # Verify time
```

#### "Connection refused" on port 6443

**Cause**: API server not ready yet

**Solution**:
```bash
# Wait for API server to start
kubectl get nodes -A         # May fail initially
sleep 30
kubectl get nodes            # Should work after master init

# Check master logs
ssh ubuntu@10.0.32.10
sudo journalctl -u kubelet -n 50
sudo journalctl -u kubeadm -n 50
```

### Reboot Issues

**Problem**: System doesn't come back online after reboot

**Diagnosis**:
```bash
# Try to ping the node
ping 10.0.32.10

# Check if node is running
# Via vSphere/hypervisor console

# Check console for errors (GRUB, kernel panic, etc.)
```

**Solutions**:
1. Verify GRUB configuration applied correctly
   ```bash
   # On node:
   cat /etc/default/grub | grep GRUB_CMDLINE_LINUX
   # Should show: apparmor=0 security=apparmor audit=1
   ```

2. Check kernel logs
   ```bash
   dmesg | tail -20
   ```

3. Verify disk space before reboot
   ```bash
   df -h
   # If low, clean up:
   apt clean
   apt autoclean
   ```

### Kubeadm Init Failures

**Error**: `[init] Using Kubernetes version: ...`
**Then**: `error execution phase ...`

**Causes**:

1. **Insufficient system resources**
   ```bash
   # Check resources
   free -h                    # Memory
   df -h /var               # Disk space
   
   # Minimum requirements:
   # - 2GB RAM per master
   # - 10GB disk space
   ```

2. **Port already in use**
   ```bash
   # Check ports
   sudo netstat -tulpn | grep LISTEN | grep 6443
   
   # Stop conflicting services
   sudo systemctl stop <service>
   ```

3. **Kubelet not running**
   ```bash
   # Check kubelet status
   systemctl status kubelet
   
   # Enable and start
   sudo systemctl enable kubelet
   sudo systemctl start kubelet
   
   # Check logs
   journalctl -u kubelet -n 50
   ```

**Solution**:
```bash
# Reset and retry
sudo kubeadm reset --force
sudo rm -rf /etc/kubernetes /var/lib/etcd
sudo systemctl restart kubelet

# Then rerun playbook
```

### Master Node Join Issues

**Error**: `certificate verification failed`

**Cause**: Certificate key expired or invalid

**Solution**:
```bash
# On first master, generate new certificate key
sudo kubeadm init phase upload-certs --upload-certs

# Get updated join command with new cert key
kubeadm token create --print-join-command
```

### Worker Node Join Issues

**Error**: `Unable to connect to 172.23.60.153:6443`

**Causes**:

1. **VIP not accessible from workers**
   ```bash
   # Test from worker node
   nc -zv 172.23.60.153 6443
   ping 172.23.60.153
   ```

2. **F5 VIP not configured**
   ```bash
   # Verify F5 configuration:
   # - Virtual IP created: 172.23.60.153
   # - Port 6443 configured
   # - Back-end pool pointing to masters
   # - Pool members healthy
   ```

3. **Firewall blocking connection**
   ```bash
   # Check firewall rules
   sudo ufw status
   sudo iptables -L -n | grep 6443
   ```

**Solution**:
```bash
# Verify API server accessibility from worker
curl -k https://172.23.60.153:6443/api/v1/nodes

# If fails, check F5:
# 1. Verify VIP IP and port
# 2. Check pool member health
# 3. Verify network routing
# 4. Check security groups/firewall
```

## Post-Deployment Issues

### Nodes Not Ready

**Error**: `kubectl get nodes` shows NotReady status

**Causes**:

1. **CNI not deployed**
   ```bash
   # Check if Calico is installed
   kubectl get pods -n calico-system
   
   # If not, deploy:
   kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.31.3/manifests/operator-crds.yaml
   ```

2. **Kubelet issues**
   ```bash
   # Check kubelet status on node
   ssh ubuntu@10.0.32.2
   systemctl status kubelet
   journalctl -u kubelet -n 50
   
   # Common fixes:
   sudo systemctl restart kubelet
   sudo systemctl restart containerd
   ```

3. **Network connectivity**
   ```bash
   # Check node-to-node connectivity
   ssh ubuntu@10.0.32.10 ping 10.0.32.2
   ```

**Diagnostic**:
```bash
# Get node details
kubectl describe node vmw1

# Check node logs
kubectl logs -n kube-system --all-containers=true

# Check events
kubectl get events --all-namespaces --sort-by='.lastTimestamp'
```

### Calico Pods Not Starting

**Symptoms**: Pods stuck in `Pending` or `CrashLoopBackOff`

**Diagnosis**:
```bash
# Check Calico pod status
kubectl get pods -n calico-system -o wide

# Check pod logs
kubectl logs -n calico-system <pod-name> -c calico-node

# Check for errors
kubectl describe pod -n calico-system <pod-name>
```

**Solutions**:

1. **Tigera operator not running**
   ```bash
   # Verify operator
   kubectl get deployment -n tigera-operator
   
   # If missing, create it:
   kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.31.3/manifests/tigera-operator.yaml
   ```

2. **Custom resources misconfigured**
   ```bash
   # Check installation
   kubectl get installation -n calico-system
   kubectl describe installation -n calico-system
   
   # Check for errors
   kubectl logs -n tigera-operator -l k8s-app=tigera-operator
   ```

3. **Pod network CIDR mismatch**
   ```bash
   # Verify config matches
   grep pod_cidr config/cluster-config.yaml
   
   # Check Calico pool
   kubectl get ippools -n calico-system
   ```

### DNS Not Working

**Error**: Pod cannot resolve cluster DNS

**Test DNS**:
```bash
# From pod
kubectl run -it busybox --image=busybox --restart=Never -- nslookup kubernetes.default

# From node
systemctl status systemd-resolved
```

**Solutions**:

1. **CoreDNS pods not running**
   ```bash
   # Check CoreDNS
   kubectl get pods -n kube-system -l k8s-app=kube-dns
   
   # If not running, check events
   kubectl describe pod -n kube-system <coredns-pod>
   ```

2. **Network connectivity between nodes**
   ```bash
   # Test node-to-node DNS
   ssh ubuntu@10.0.32.10 nslookup 8.8.8.8
   ```

### Persistent Storage Issues

**Error**: PVC stays in `Pending`

**Cause**: No storage class defined

**Solution**:
```bash
# Check storage classes
kubectl get storageclass

# Calico doesn't provide storage, install:
# - Local volumes
# - NFS provisioner
# - Cloud provider storage (if applicable)
```

## Log Collection

### Collect Deployment Logs

```bash
# From GitLab CI job logs
# Click job → Download artifacts

# From nodes
ssh ubuntu@10.0.32.10

# Kubernetes logs
journalctl -u kubelet > kubelet.log
journalctl -u kubeadm > kubeadm.log
kubectl logs -n kube-system --all-containers=true > kube-system.log

# Container runtime logs
journalctl -u docker > docker.log
journalctl -u containerd > containerd.log

# System logs
dmesg > kernel.log
syslog
```

### Debug Commands

```bash
# Check all pods
kubectl get pods --all-namespaces

# Check failed pods
kubectl get pods --all-namespaces --field-selector=status.phase!=Running

# Get pod details
kubectl describe pod <pod-name> -n <namespace>

# Get pod logs
kubectl logs <pod-name> -n <namespace>

# Get previous pod logs (if restarted)
kubectl logs <pod-name> -n <namespace> --previous

# Check events
kubectl get events --all-namespaces --sort-by='.lastTimestamp'

# Check node status
kubectl describe node <node-name>

# Check cluster info
kubectl cluster-info dump > cluster-dump.tar.gz
```

## Recovery Procedures

### Restart Failed Master

```bash
# SSH to master node
ssh ubuntu@10.0.32.10

# Stop services
sudo systemctl stop kubelet
sudo systemctl stop docker
sudo systemctl stop containerd

# Reset kubeadm
sudo kubeadm reset --force

# Clean up
sudo rm -rf /etc/kubernetes /var/lib/etcd

# Start services
sudo systemctl start containerd
sudo systemctl start docker
sudo systemctl start kubelet

# Rejoin to cluster (follow join command from first master)
```

### Restore from Etcd Backup

```bash
# On first master with healthy etcd
sudo ETCDCTL_API=3 etcdctl snapshot save /tmp/etcd-backup.db

# Copy to safe location
scp ubuntu@10.0.32.10:/tmp/etcd-backup.db ./

# To restore (on new master):
sudo systemctl stop kube-apiserver
sudo ETCDCTL_API=3 etcdctl snapshot restore /tmp/etcd-backup.db \
  --data-dir=/var/lib/etcd-restore
sudo systemctl start kube-apiserver
```

## Getting Help

### Information to Provide

When requesting help, provide:
1. Full error message and context
2. Configuration file (sanitized)
3. Pipeline logs
4. Node logs (kubelet, kubeadm)
5. Kubernetes cluster info: `kubectl cluster-info dump`
6. Output of: `kubectl get nodes`, `kubectl get pods --all-namespaces`

### Support Resources

- Kubernetes docs: https://kubernetes.io/docs/
- Calico docs: https://docs.tigera.io/
- Ansible docs: https://docs.ansible.com/
- Ubuntu docs: https://ubuntu.com/server/docs/

## Prevention Tips

1. **Monitor cluster health** - Set up monitoring/alerting
2. **Regular backups** - Backup etcd regularly
3. **Test procedures** - Regularly test recovery procedures
4. **Keep logs** - Archive pipeline and system logs
5. **Document changes** - Track configuration changes
6. **Review updates** - Test Kubernetes updates in dev first
7. **Security scanning** - Regularly scan for vulnerabilities
