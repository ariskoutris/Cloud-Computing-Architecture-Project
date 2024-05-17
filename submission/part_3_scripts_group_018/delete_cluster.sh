#!/bin/bash

echo "Deleting the cluster..."
export KOPS_STATE_STORE=gs://cca-eth-2024-group-018-mtsanta/
kops delete cluster part3.k8s.local --yes
echo "Cluster deleted."