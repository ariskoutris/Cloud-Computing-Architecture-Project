#!/bin/bash
export KOPS_STATE_STORE=gs://cca-eth-2024-group-018-mtsanta/
CLUSTER_NAME="part3.k8s.local"
PROJECT=`gcloud config get-value project`

echo "Creating a new cluster in project ${PROJECT}..."
kops create -f part3.yaml

# Update the cluster and apply the changes
echo "Updating and applying changes to the cluster..."
kops update cluster --name part3.k8s.local --yes --admin

# Check the exit status of the kops update cluster command
if [ $? -ne 0 ]; then
    echo "Cluster update failed. Exiting..."
    exit 1
fi

# Validate the cluster
# This command will retry for up to 10 minutes to validate the cluster
echo "Validating the cluster, this might take up to 10 minutes..."
kops validate cluster --wait 10m

# Check the exit status of the kops validate cluster command
if [ $? -eq 0 ]; then
    echo "Cluster validation successful. Retrieving node information..."
    kubectl get nodes -o wide
else
    echo "Cluster validation failed. Please check the cluster status and try again."
    exit 1
fi
