#!/bin/bash

echo "Deleting the cluster..."
kops delete cluster part2a.k8s.local --yes
echo "Cluster deleted."