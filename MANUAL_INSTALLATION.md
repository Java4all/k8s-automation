
## MANUAL PLAYBOOK EXECUTION 

1. Extract & Setup
   $ tar -xzf k8s-automation.tar.gz
   $ cd k8s-automation

2. Configure
   $ cp config/cluster-config.example.yaml config/cluster-config.yaml
   $ nano config/cluster-config.yaml
   # Edit with your environment details

3. Generate Inventory
   $ python3 inventories/inventory.py --config config/cluster-config.yaml > inventory.json

4. Test Connectivity
   $ ansible -i inventory.json all -m ping

5. Run Playbook
   $ ansible-playbook \
       --inventory inventory.json \
       --extra-vars '@config/cluster-config.yaml' \
       playbooks/deploy-k8s-cluster.yml \
       -v


## USEFUL COMMANDS

# Test specific role (no risk, no changes with --check)
ansible-playbook -i inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --tags common --check -v

# Run only on masters
ansible-playbook -i inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --limit masters -v

# Test connectivity
ansible -i inventory.json all -m ping

# Dry run (no changes)
ansible-playbook -i inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --check -v

# Maximum verbosity (for debugging)
ansible-playbook -i inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  -vvvv

# Step through (interactive, pause at each task)
ansible-playbook -i inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --step -v

# View all tasks before running
ansible-playbook -i inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  --list-tasks

# Save output to file
ansible-playbook -i inventory.json \
  --extra-vars '@config/cluster-config.yaml' \
  playbooks/deploy-k8s-cluster.yml \
  -v 2>&1 | tee deployment.log
