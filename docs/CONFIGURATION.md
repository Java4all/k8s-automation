# Configuration Reference Guide

Complete reference for all configuration parameters in `cluster-config.yaml`.

## Structure Overview

```
cluster
├── name
├── environment
├── k8s_version
├── control_plane
├── networking
├── proxy
├── calico
└── system

nodes
├── masters
└── workers

container_runtime
ssh
deployment
```

## Cluster Configuration

### cluster.name
**Type**: String  
**Default**: `production-k8s`  
**Description**: Unique identifier for the Kubernetes cluster

```yaml
cluster:
  name: "production-k8s"  # Should be unique across deployments
```

### cluster.environment
**Type**: String  
**Valid Values**: `dev`, `staging`, `prod`  
**Default**: `prod`  
**Description**: Deployment environment

```yaml
cluster:
  environment: "prod"  # Affects logging and monitoring levels
```

### cluster.k8s_version
**Type**: String (version number)  
**Default**: `1.34`  
**Description**: Kubernetes version to deploy

```yaml
cluster:
  k8s_version: "1.34"  # Version must be available in k8s repos

  # Supported versions:
  # 1.30, 1.31, 1.32, 1.33, 1.34 (and newer)
```

### cluster.control_plane Configuration

#### endpoint_vip
**Type**: IP Address  
**Default**: `172.23.60.153`  
**Description**: Virtual IP address for load-balanced API server access  
**Important**: Must be configured on F5 or other load balancer

```yaml
cluster:
  control_plane:
    endpoint_vip: "172.23.60.153"  # F5 VIP, not a master node IP
```

#### endpoint_port
**Type**: Integer  
**Default**: `6443`  
**Description**: API server port

```yaml
cluster:
  control_plane:
    endpoint_port: 6443  # Standard Kubernetes API port
```

## Network Configuration

### cluster.networking.pod_cidr
**Type**: CIDR Block  
**Default**: `10.0.68.0/21`  
**Description**: Network range for pod-to-pod communication

```yaml
cluster:
  networking:
    pod_cidr: "10.0.68.0/21"  # 8 subnets, 2046 IPs
    
    # Sizing guide:
    # /24 = 254 IPs (small clusters)
    # /21 = 2046 IPs (medium clusters)
    # /16 = 65534 IPs (large clusters)
```

### cluster.networking.service_cidr
**Type**: CIDR Block  
**Default**: `10.0.76.0/22`  
**Description**: Network range for Kubernetes Services (ClusterIP)

```yaml
cluster:
  networking:
    service_cidr: "10.0.76.0/22"  # Default: 10.0.0.0/24
    
    # Must be different from:
    # - Pod CIDR
    # - Node network (10.0.32.0/20)
    # - Any existing cluster networks
```

### cluster.networking.dns_servers
**Type**: List of IP Addresses  
**Default**: `[8.8.8.8, 8.8.4.4]`  
**Description**: DNS servers for node resolution

```yaml
cluster:
  networking:
    dns_servers:
      - "8.8.8.8"              # Google DNS
      - "8.8.4.4"
      # Or corporate DNS:
      # - "10.0.1.1"
      # - "10.0.1.2"
```

### cluster.networking.ntp_servers
**Type**: List of Hostnames/IPs  
**Default**: Ubuntu NTP pools  
**Description**: NTP servers for time synchronization

```yaml
cluster:
  networking:
    ntp_servers:
      - "0.ubuntu.pool.ntp.org"
      - "1.ubuntu.pool.ntp.org"
      # Or internal NTP:
      # - "ntp.company.com"
```

## Proxy Configuration

### cluster.proxy.enabled
**Type**: Boolean  
**Default**: `true`  
**Description**: Enable/disable proxy configuration

```yaml
cluster:
  proxy:
    enabled: true   # Apply proxy to container runtimes and kubelet
```

### cluster.proxy.http_proxy
**Type**: URL  
**Required if**: `proxy.enabled: true`  
**Description**: HTTP proxy URL

```yaml
cluster:
  proxy:
    http_proxy: "http://10.0.0.254:8080"
    # Format: http://proxy-host:proxy-port
    # Can include authentication: http://user:pass@proxy:port
```

### cluster.proxy.https_proxy
**Type**: URL  
**Required if**: `proxy.enabled: true`  
**Description**: HTTPS proxy URL

```yaml
cluster:
  proxy:
    https_proxy: "http://10.0.0.254:8080"  # Often same as http_proxy
```

### cluster.proxy.no_proxy_list
**Type**: List of addresses/networks  
**Description**: Hosts to bypass proxy

```yaml
cluster:
  proxy:
    no_proxy_list:
      - "localhost"
      - "127.0.0.1"
      - "localaddress"
      - ".localdomain.com"
      - ".local"
      - "10.0.0.0/8"
      - "192.168.0.0/16"
      - "172.16.0.0/12"
      - ".cluster"
      - "127.0.0.0/8"
      
      # Add internal domains:
      # - "company.com"
      # - ".company.local"
      # - "kubernetes.default.svc"
```

## Calico Configuration

### cluster.calico.version
**Type**: String (version tag)  
**Default**: `v3.31.3`  
**Description**: Calico network plugin version

```yaml
cluster:
  calico:
    version: "v3.31.3"  # Check: https://github.com/projectcalico/calico/releases
```

### cluster.calico.pool_cidr
**Type**: CIDR Block  
**Default**: Same as `cluster.networking.pod_cidr`  
**Description**: Calico IP pool configuration

```yaml
cluster:
  calico:
    pool_cidr: "10.0.68.0/21"  # Must match pod_cidr
```

## System Configuration

### cluster.system.os
**Type**: String  
**Default**: `Ubuntu 24.04.3 LTS`  
**Description**: Operating system (informational)

```yaml
cluster:
  system:
    os: "Ubuntu 24.04.3 LTS"
```

### cluster.system.timezone
**Type**: String (IANA timezone)  
**Default**: `UTC`  
**Description**: System timezone for all nodes

```yaml
cluster:
  system:
    timezone: "UTC"
    # Common options:
    # "America/New_York"
    # "Europe/London"
    # "Asia/Tokyo"
```

### cluster.system.disable_apparmor
**Type**: Boolean  
**Default**: `true`  
**Description**: Disable AppArmor SELinux enforcement

```yaml
cluster:
  system:
    disable_apparmor: true  # Required for Kubernetes
```

### cluster.system.disable_swap
**Type**: Boolean  
**Default**: `true`  
**Description**: Disable swap memory

```yaml
cluster:
  system:
    disable_swap: true  # Required for Kubernetes
```

## Container Runtime Configuration

### container_runtime.engine
**Type**: String  
**Default**: `containerd`  
**Valid Values**: `containerd` (only option currently)

```yaml
container_runtime:
  engine: "containerd"
```

### container_runtime.docker_enabled
**Type**: Boolean  
**Default**: `true`  
**Description**: Install Docker.io alongside containerd

```yaml
container_runtime:
  docker_enabled: true  # Both can coexist
```

### container_runtime.systemd_cgroup
**Type**: Boolean  
**Default**: `true`  
**Description**: Use systemd cgroup driver

```yaml
container_runtime:
  systemd_cgroup: true  # Required for proper cgroup v2 support
```

## Node Configuration

### Node Structure

```yaml
nodes:
  masters:
    - name: "vmm1"
      hostname: "vmm1"
      ip: "10.0.32.10"
      netmask: "255.255.240.0"    # /20
      gateway: "10.0.32.1"
      role: "master"
  
  workers:
    - name: "vmw1"
      hostname: "vmw1"
      ip: "10.0.32.2"
      netmask: "255.255.240.0"    # /20
      gateway: "10.0.32.1"
      role: "worker"
```

### Master Node Parameters

#### name
**Type**: String  
**Description**: Unique identifier for the node

```yaml
- name: "vmm1"  # Used for identification in cluster
```

#### hostname
**Type**: String  
**Description**: Linux hostname for the node

```yaml
- hostname: "vmm1"  # Set via `hostnamectl set-hostname`
```

#### ip
**Type**: IP Address  
**Description**: Node's primary IP address

```yaml
- ip: "10.0.32.10"  # Must be reachable from GitLab runner
```

#### netmask
**Type**: Netmask  
**Description**: Network mask for the subnet

```yaml
- netmask: "255.255.240.0"  # /20 = 4096 IPs per subnet
```

#### gateway
**Type**: IP Address  
**Description**: Default gateway

```yaml
- gateway: "10.0.32.1"  # Default route
```

## SSH Configuration

### ssh.user
**Type**: String  
**Default**: `ubuntu`  
**Description**: SSH user for node access

```yaml
ssh:
  user: "ubuntu"  # User that can run sudo without password
```

### ssh.key_path
**Type**: Path  
**Default**: `/root/.ssh/id_rsa`  
**Description**: Path to SSH private key on GitLab runner

```yaml
ssh:
  key_path: "/root/.ssh/id_rsa"  # Set via SSH_PRIVATE_KEY variable
```

### ssh.port
**Type**: Integer  
**Default**: `22`  
**Description**: SSH port

```yaml
ssh:
  port: 22  # Standard SSH port
```

### ssh.timeout
**Type**: Integer (seconds)  
**Default**: `300`  
**Description**: SSH connection timeout

```yaml
ssh:
  timeout: 300  # 5 minutes
```

### ssh.retries
**Type**: Integer  
**Default**: `3`  
**Description**: SSH connection retry attempts

```yaml
ssh:
  retries: 3  # Retry 3 times before failing
```

## Deployment Options

### deployment.skip_verification
**Type**: Boolean  
**Default**: `false`  
**Description**: Skip post-deployment verification

```yaml
deployment:
  skip_verification: false  # Always verify deployment
```

### deployment.health_check_timeout
**Type**: Integer (seconds)  
**Default**: `600`  
**Description**: Timeout for health checks

```yaml
deployment:
  health_check_timeout: 600  # 10 minutes
```

### deployment.calico_wait_timeout
**Type**: Integer (seconds)  
**Default**: `300`  
**Description**: Timeout for Calico pods to be ready

```yaml
deployment:
  calico_wait_timeout: 300  # 5 minutes
```

### deployment.parallel_workers
**Type**: Integer  
**Default**: `3`  
**Description**: Number of worker nodes to deploy in parallel

```yaml
deployment:
  parallel_workers: 3  # Deploy up to 3 workers simultaneously
  # Use 1 for serial deployment
```

## Example Configurations

### Minimal Configuration

```yaml
cluster:
  name: "k8s-cluster"
  k8s_version: "1.34"
  control_plane:
    endpoint_vip: "172.23.60.153"
  networking:
    pod_cidr: "10.0.68.0/21"
  proxy:
    enabled: false

nodes:
  masters:
    - name: "vmm1"
      ip: "10.0.32.10"
```

### Production Configuration

```yaml
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
      - "10.0.1.1"
      - "10.0.1.2"
    ntp_servers:
      - "ntp.company.com"
  proxy:
    enabled: true
    http_proxy: "http://corp-proxy.com:8080"
    https_proxy: "http://corp-proxy.com:8080"
    no_proxy_list:
      - "localhost"
      - "127.0.0.1"
      - "10.0.0.0/8"
      - ".company.com"
  calico:
    version: "v3.31.3"
    pool_cidr: "10.0.68.0/21"

nodes:
  masters:
    - name: "vmm1"
      hostname: "vmm1"
      ip: "10.0.32.10"
      netmask: "255.255.240.0"
      gateway: "10.0.32.1"
    - name: "vmm2"
      hostname: "vmm2"
      ip: "10.0.32.11"
      netmask: "255.255.240.0"
      gateway: "10.0.32.1"
    - name: "vmm3"
      hostname: "vmm3"
      ip: "10.0.32.12"
      netmask: "255.255.240.0"
      gateway: "10.0.32.1"
  
  workers:
    - name: "vmw1"
      hostname: "vmw1"
      ip: "10.0.32.2"
      netmask: "255.255.240.0"
      gateway: "10.0.32.1"
    - name: "vmw2"
      hostname: "vmw2"
      ip: "10.0.32.3"
      netmask: "255.255.240.0"
      gateway: "10.0.32.1"
    - name: "vmw3"
      hostname: "vmw3"
      ip: "10.0.32.4"
      netmask: "255.255.240.0"
      gateway: "10.0.32.1"

deployment:
  skip_verification: false
  health_check_timeout: 600
  calico_wait_timeout: 300
  parallel_workers: 2
```

## Validation Tips

1. **CIDR Validation**
   ```bash
   python3 -c "from ipaddress import ip_network; ip_network('10.0.68.0/21')"
   ```

2. **IP Address Validation**
   ```bash
   python3 -c "from ipaddress import ip_address; ip_address('10.0.32.10')"
   ```

3. **YAML Syntax Validation**
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('config/cluster-config.yaml'))"
   ```

4. **Duplicate IPs**
   ```bash
   # Check for duplicate IPs in configuration
   grep -E "^\s+ip:" config/cluster-config.yaml | sort | uniq -d
   ```
