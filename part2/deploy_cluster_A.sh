#!/bin/bash

CLUSTER_NAME="part2a.k8s.local"
PROJECT=`gcloud config get-value project`

echo "Creating a new cluster in project ${PROJECT}..."
kops create -f part2a.yaml

# Update the cluster and apply the changes
echo "Updating and applying changes to the cluster..."
kops update cluster --name ${CLUSTER_NAME} --yes --admin

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

# Label the parsec server nodes
PARSEC_SERVER_NAME=$(kubectl get nodes -o wide | grep -i parsec | awk '{print $1}')
kubectl label nodes ${PARSEC_SERVER_NAME} cca-project-nodetype=parsec
