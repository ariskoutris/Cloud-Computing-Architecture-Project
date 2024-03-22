#!/bin/bash

export KOPS_STATE_STORE=gs://cca-eth-2024-group-018-akoutris/

echo "Deleting the cluster..."
kops delete cluster part1.k8s.local --yes
echo "Cluster deleted."