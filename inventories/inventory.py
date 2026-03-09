#!/usr/bin/env python3
"""
Dynamic inventory script that generates inventory from cluster config YAML
Usage: python3 inventory.py --config /path/to/cluster-config.yaml
"""

import argparse
import yaml
import json
import sys
from ipaddress import IPv4Network

def netmask_to_cidr(netmask):
    """Convert netmask to CIDR prefix"""
    try:
        return str(IPv4Network(f'0.0.0.0/{netmask}').prefixlen)
    except:
        # Default to /20 if conversion fails (255.255.240.0 = /20)
        return '20'

def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def generate_inventory(config):
    inventory = {
        'all': {
            'hosts': {},
            'children': {'masters': {}, 'workers': {}}
        },
        'masters': {
            'hosts': {}
        },
        'workers': {
            'hosts': {}
        },
        '_meta': {
            'hostvars': {}
        }
    }
    
    # Add master nodes
    if 'masters' in config['nodes']:
        for master in config['nodes']['masters']:
            host = master['name']
            master_host_config = {
                'ansible_host': master['ip'],
                'ansible_user': config['ssh']['user']
            }
            # Add SSH key if specified for this node
            if 'ssh_key_file' in master:
                master_host_config['ansible_ssh_private_key_file'] = master['ssh_key_file']
            
            inventory['masters']['hosts'][host] = master_host_config
            inventory['all']['hosts'][host] = master_host_config
            
            inventory['_meta']['hostvars'][host] = {
                'ansible_host': master['ip'],
                'ansible_user': config['ssh']['user'],
                'node_ip': master['ip'],
                'node_role': 'master',
                'cidr_prefix': netmask_to_cidr(master.get('netmask', '255.255.240.0'))
            }
            # Add SSH key to hostvars if specified
            if 'ssh_key_file' in master:
                inventory['_meta']['hostvars'][host]['ansible_ssh_private_key_file'] = master['ssh_key_file']
    
    # Add worker nodes
    if 'workers' in config['nodes']:
        for worker in config['nodes']['workers']:
            host = worker['name']
            worker_host_config = {
                'ansible_host': worker['ip'],
                'ansible_user': config['ssh']['user']
            }
            # Add SSH key if specified for this node
            if 'ssh_key_file' in worker:
                worker_host_config['ansible_ssh_private_key_file'] = worker['ssh_key_file']
            
            inventory['workers']['hosts'][host] = worker_host_config
            inventory['all']['hosts'][host] = worker_host_config
            
            inventory['_meta']['hostvars'][host] = {
                'ansible_host': worker['ip'],
                'ansible_user': config['ssh']['user'],
                'node_ip': worker['ip'],
                'node_role': 'worker',
                'cidr_prefix': netmask_to_cidr(worker.get('netmask', '255.255.240.0'))
            }
            # Add SSH key to hostvars if specified
            if 'ssh_key_file' in worker:
                inventory['_meta']['hostvars'][host]['ansible_ssh_private_key_file'] = worker['ssh_key_file']
    
    return inventory

def main():
    parser = argparse.ArgumentParser(
        description='Generate Ansible inventory from Kubernetes cluster config'
    )
    parser.add_argument('--config', required=True, help='Path to cluster config YAML file')
    parser.add_argument('--list', action='store_true', default=True, help='List all hosts')
    parser.add_argument('--host', help='Get specific host details')
    
    args = parser.parse_args()
    
    try:
        config = load_config(args.config)
        inventory = generate_inventory(config)
        
        if args.host:
            # Return specific host vars
            if args.host in inventory['_meta']['hostvars']:
                print(json.dumps(inventory['_meta']['hostvars'][args.host]))
            else:
                print(json.dumps({}))
        else:
            # Return full inventory
            print(json.dumps(inventory, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
