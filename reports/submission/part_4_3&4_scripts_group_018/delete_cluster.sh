#!/bin/bash
echo "Deleting the cluster..."
kops delete cluster --name part4.k8s.local --yes
echo "Cluster deleted."