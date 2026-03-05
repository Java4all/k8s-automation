#!/usr/bin/env python3
"""
Dynamic inventory script that generates inventory from cluster config YAML
Usage: python3 inventory.py --config /path/to/cluster-config.yaml
"""

import argparse
import yaml
import json
import sys

def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def generate_inventory(config):
    inventory = {
        'all': {
            'hosts': {},
            'children': ['masters', 'workers']
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
            inventory['masters']['hosts'][host] = {
                'ansible_host': master['ip'],
                'ansible_user': config['ssh']['user']
            }
            inventory['all']['hosts'][host] = {
                'ansible_host': master['ip'],
                'ansible_user': config['ssh']['user']
            }
            inventory['_meta']['hostvars'][host] = {
                'ansible_host': master['ip'],
                'ansible_user': config['ssh']['user'],
                'node_ip': master['ip'],
                'node_role': 'master'
            }
    
    # Add worker nodes
    if 'workers' in config['nodes']:
        for worker in config['nodes']['workers']:
            host = worker['name']
            inventory['workers']['hosts'][host] = {
                'ansible_host': worker['ip'],
                'ansible_user': config['ssh']['user']
            }
            inventory['all']['hosts'][host] = {
                'ansible_host': worker['ip'],
                'ansible_user': config['ssh']['user']
            }
            inventory['_meta']['hostvars'][host] = {
                'ansible_host': worker['ip'],
                'ansible_user': config['ssh']['user'],
                'node_ip': worker['ip'],
                'node_role': 'worker'
            }
    
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
