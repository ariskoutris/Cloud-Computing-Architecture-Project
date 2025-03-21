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

</div>

## Overview

This project explores cloud computing performance optimization by focusing on resource allocation, scheduling policies, and interference management in containerized environments. Both latency-sensitive services and batch processing applications are orchestrated using Kubernetes and Docker. Developed for the Cloud Computing Architecture course at ETH Zurich.

## Setup

Ensure you have installed `kubectl`, `kops`, and `gcloud` and validate their installation.

```bash
$ kubectl --help
$ kops --help
$ gcloud --help
```

Initialize your project.

```bash
$ gcloud init
```

Create a Google Cloud bucket for cluster configurations.

```bash
$ gsutil mb gs://bucket-example/
$ export KOPS_STATE_STORE=gs://bucket-example/
```

Additionally, make sure to replace your bucket address on the `spec.configBase` field, in the following configuration files: [part1.yaml](part1/part1.yaml), [part2a.yaml](part2/part2a.yaml), [part2b.yaml](part2/part2b.yaml), [part3.yaml](part3/part3.yaml), [part4.yaml](part4/part4.yaml)

## Structure
The project is organized into four main parts:

### Part 1: Basic Performance Analysis
This part focuses on performing a memcached microbenchmark on the cluster with various types of interference. The goal is to understand how different interferences affect cluster performance.

To run the benchmark, sequentially run the following commands, to deploy the cluster, setup the benchmark, run the benchmark and then delete the cluster:
```bash
$ cd part1
$ ./deploy_cluster.sh
$ ./setup_benchmark.sh
$ ./run_benchmark.sh
$ ./delete_cluster.sh
```

### Part 2: Interference Analysis

This part focuses on running various workloads from the PARSEC benchmark suite and analyzing their sensitivity to various parameters. For part 2A, various types of interference are set into place, to investigate how they affect performance. For part 2B, execution is split onto multiple threads to study the impact of parallelism. 

To run the benchmarks, replace {X} with either A or B for parts 2A and 2B respectivelly, and sequentially run the following commands, to deploy the cluster, run the benchmark and then delete the cluster:
```bash
$ cd part2
$ ./deploy_cluster_{X}.sh
$ ./run_benchmark_{X}.sh
$ ./delete_cluster_{X}.sh
```

### Part 3: Co-scheduling with Performance Objectives

This part focuses on scheduling both latency-critical and batch applications within a heterogeneous Kubernetes cluster. A scheduling policy that considers application characteristics, resource requirements, and interference patterns ensures that the execution times remains low, while memcached meets its strict service level objective (95th percentile latency under 1ms at 30K QPS).

To run the benchmark, sequentially run the following commands:
```bash
$ cd part3
$ ./deploy_cluster.sh
$ ./setup_memcached.sh
$ ./run_benchmark.sh
$ ./delete_cluster.sh
```

### Part 4: Dynamic Resource Management with Varying Workloads

This part focuses on developing a dynamic resource allocation system that responds to changing workload conditions. A custom controller co-schedules batch applications with a memcached service on a single 4-core server, where the memcached load varies over time (requiring between 1-2 cores to meet its SLO). The controller opportunistically uses temporarily available cores to complete batch jobs as quickly as possible while guaranteeing memcached's tail latency SLO of 1ms 95th percentile latency. Unlike previous parts, this section uses Docker instead of Kubernetes to enable real-time adjustment of resource allocations.

To run the benchmark, sequentially run the following commands:
```bash
$ cd part4
$ ./deploy_cluster.sh
$ ./setup_memcached.sh
$ ./memcached_benchmark.sh
$ ./delete_cluster.sh
```

## Team Members
* Aris Koutris, [akoutris@ethz.ch](mailto:akoutris@ethz.ch)
* George Manos,  [gmanos@ethz.ch](mailto:gmanos@ethz.ch)
* Maritina Tsanta, [mtsanta@ethz.ch](mailto:mtsanta@ethz.ch)
