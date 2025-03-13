<div align="center">

  <img src="assets/systems-logo.png">
  
# Cloud Computer Architecture
### Spring Semester 2024
### Professor: [Ana Klimovic](https://anakli.inf.ethz.ch)


<a href="#">
    <img src="https://img.shields.io/badge/Python-3.10-1cb855">
</a>
<a href="#">
    <img src="https://img.shields.io/badge/Kubernetes-v1.29.2-0388fc">
</a>
<a href="#">
    <img src="https://img.shields.io/badge/Cloud-Google-F4B400">
</a>
<br>
<a href="#">
    <img src="https://img.shields.io/badge/License-MIT-8a0023">
</a>
<br>
<a href="https://systems.ethz.ch/education/courses/2024-spring/cloud-computing-architecture.html"><strong>Explore Course Page »</strong></a>
</div>

## Description

This project explores cloud computing performance optimization, focusing on resource allocation, scheduling, and interference management in containerized environments. It was developed for the Cloud Computing Architecture course at ETH Zurich.

## Structure
The project is organized into four main parts:

### Part 1: Basic Performance Analysis
This part focuses on performing a memcached microbenchmark on the cluster with various types of interference. The goal is to understand how different interferences affect cluster performance.

To run the benchmark, sequentially run the following commands, to deploy the cluster, setup the benchmark, run the benchmark and then delete the cluster:
```bash
$ cd part1
$ export KOPS_STATE_STORE=gs://cca-eth-2024-group-018-ethid/
$ ./deploy_cluster.sh
$ ./setup_benchmark.sh
$ ./run_benchmark.sh
$ ./delete_cluster.sh
```

Note:
The cluster configuration is stored in the bucket `gs://cca-eth-2024-group-018-ethzid`. Make sure to replace `ethzid` with your ETH username in the following file: [part1.yaml](part1/part1.yaml)

### Part 2: Interference Analysis

This part focuses on running various workloads from the PARSEC benchmark suite and analyzing their sensitivity to various parameters. For part 2A, various types of interference are set into place, to investigate how they affect performance. For part 2B, execution is split onto multiple threads to study the impact of parallelism. 

To run the benchmarks, replace {X} with either A or B for parts 2A and 2B respectivelly, and sequentially run the following commands, to deploy the cluster, run the benchmark and then delete the cluster:
```bash
$ cd part2
$ export KOPS_STATE_STORE=gs://cca-eth-2024-group-018-<ethid>/
$ ./deploy_cluster_{X}.sh
$ ./run_benchmark_{X}.sh
$ ./delete_cluster_{X}.sh
```
Note:
The cluster configuration is stored in the bucket `gs://cca-eth-2024-group-018-ethzid`. Make sure to replace `ethzid` with your ETH username in the following files: [part2a.yaml](part2/part2a.yaml), [part2b.yaml](part2/part2b.yaml)

### Part 3: Co-scheduling with Performance Objectives

This part focuses on scheduling both latency-critical and batch applications within a heterogeneous Kubernetes cluster. You will co-schedule the memcached service from Part 1 with all seven PARSEC benchmark applications from Part 2 on a cluster with different VM types (2, 4, and 8 cores). The goal is to minimize the total execution time (makespan) of all batch jobs while ensuring memcached meets its strict service level objective (95th percentile latency under 1ms at 30K QPS). This requires developing an effective scheduling policy that considers application characteristics, resource requirements, and interference patterns.

To run the benchmark, sequentially run the following commands:
```bash
$ cd part3
$ export KOPS_STATE_STORE=gs://cca-eth-2024-group-018-<ethid>/
$ ./deploy_cluster.sh
$ ./setup_memcached.sh
$ ./run_benchmark.sh
$ ./delete_cluster.sh
```
Note: The cluster configuration is stored in the bucket gs://cca-eth-2024-group-018-ethzid. Make sure to replace ethzid with your ETH username in the following file: [part3.yaml](part3/part3.yaml)

### Part 4: Dynamic Resource Management with Varying Workloads

This part focuses on developing a dynamic resource allocation system that responds to changing workload conditions. You'll implement a custom controller to co-schedule batch applications with a memcached service on a single 4-core server, where the memcached load varies over time (requiring between 1-2 cores to meet its SLO). The goal is to opportunistically use temporarily available cores to complete batch jobs as quickly as possible while guaranteeing memcached's tail latency SLO of 1ms 95th percentile latency. Unlike previous parts, this section uses Docker instead of Kubernetes to enable real-time adjustment of resource allocations.

To run the benchmark, sequentially run the following commands:
```bash
$ cd part4
$ export KOPS_STATE_STORE=gs://cca-eth-2024-group-018-<ethid>/
$ ./deploy_cluster.sh
$ ./setup_memcached.sh
$ ./memcached_benchmark.sh
$ ./delete_cluster.sh
```
Note: The cluster configuration is stored in the bucket gs://cca-eth-2024-group-018-ethzid. Make sure to replace ethzid with your ETH username in the following file: [part4.yaml](part4/part4.yaml)

#### Team Members:
* Aris Koutris, [akoutris@ethz.ch](mailto:akoutris@ethz.ch)
* George Manos,  [gmanos@ethz.ch](mailto:gmanos@ethz.ch)
* Maritina Tsanta, [mtsanta@ethz.ch](mailto:mtsanta@ethz.ch)
