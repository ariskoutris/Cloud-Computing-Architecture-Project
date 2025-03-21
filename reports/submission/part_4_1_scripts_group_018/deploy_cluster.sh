#!/bin/bash
CLUSTER_NAME="part4.k8s.local"
PROJECT="$(gcloud config get-value project)"

echo "Creating a new cluster in project ${PROJECT}..."
kops create -f part4.yaml

echo "Updating the cluster..."
if [ "$(kops update cluster --name $CLUSTER_NAME --yes --admin)" -ne 0 ]; then
    echo "Cluster update failed. Exiting..."
    exit 1
fi

kops validate cluster --wait 10m
kubectl get nodes -o wide

