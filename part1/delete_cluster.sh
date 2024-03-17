#!/bin/bash

echo "Deleting the cluster..."
kops delete cluster part1.k8s.local --yes
echo "Cluster deleted."