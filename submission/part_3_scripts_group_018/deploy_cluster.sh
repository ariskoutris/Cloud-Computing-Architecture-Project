#!/bin/bash
export KOPS_STATE_STORE=gs://cca-eth-2024-group-018-mtsanta/
CLUSTER_NAME="part3.k8s.local"
PROJECT="$(gcloud config get-value project)"

echo "Creating a new cluster in project ${PROJECT}..."
kops create -f part3.yaml

echo "Updating the cluster..."

if [ "$(kops update cluster --name $CLUSTER_NAME --yes --admin)" -ne 0 ]; then
    echo "Cluster update failed. Exiting..."
    exit 1
fi

kops validate cluster --wait 10m

if [ $1 -eq 0 ]; then
    echo "Cluster validation successful. Retrieving node information..."
    kubectl get nodes -o wide
else
    echo "Cluster validation failed. Please check the cluster status and try again."
    exit 1
fi
