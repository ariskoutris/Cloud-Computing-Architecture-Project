#!/bin/bash

./setup_memcached.sh
./run_mcperf.sh 1 1
./run_mcperf.sh 1 1
./run_mcperf.sh 1 1

./setup_memcached.sh
./run_mcperf.sh 1 2
./run_mcperf.sh 1 2
./run_mcperf.sh 1 2

./setup_memcached.sh
./run_mcperf.sh 2 1
./run_mcperf.sh 2 1
./run_mcperf.sh 2 1

./setup_memcached.sh
./run_mcperf.sh 2 2
./run_mcperf.sh 2 2
./run_mcperf.sh 2 2