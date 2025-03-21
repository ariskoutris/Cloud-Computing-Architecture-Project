#!/bin/bash

echo "Deleting the cluster..."
kops delete cluster part3.k8s.local --yes
echo "Cluster deleted."