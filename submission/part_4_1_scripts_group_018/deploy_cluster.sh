#!/bin/bash
export KOPS_STATE_STORE=gs://cca-eth-2024-group-018-mtsanta/
CLUSTER_NAME="part4.k8s.local"
PROJECT="$(gcloud config get-value project)"

echo "Creating a new cluster in project ${PROJECT}..."
kops create -f part4.yaml

# Update the cluster and apply the changes
echo "Updating and applying changes to the cluster..."

# Check the exit status of the kops update cluster command
if [ "$(kops update cluster --name $CLUSTER_NAME --yes --admin)" -ne 0 ]; then
    echo "Cluster update failed. Exiting..."
    exit 1
fi

echo "Validating the cluster, this might take up to 10 minutes..."
kops validate cluster --wait 10m
kubectl get nodes -o wide

