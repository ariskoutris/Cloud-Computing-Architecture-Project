#!/bin/bash

echo "Deleting the cluster..."
kops delete cluster part2b.k8s.local --yes
echo "Cluster deleted."