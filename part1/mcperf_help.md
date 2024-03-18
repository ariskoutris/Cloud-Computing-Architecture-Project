```console
Usage: mcperf -s server[@port] [options]

"High-performance" memcached benchmarking tool

  -h, --help                    Print help and exit
      --version                 Print version and exit
  -v, --verbose                 Verbosity. Repeat for more verbose.
      --quiet                   Disable log messages.

Basic options:
  -s, --server=STRING           Memcached server hostname[:port[-end_port]].
                                  Repeat to specify multiple servers. 
      --binary                  Use binary memcached protocol instead of ASCII.
  -q, --qps=INT                 Target aggregate QPS. 0 = peak QPS.
                                  (default=`0')
  -t, --time=INT                Maximum time to run (seconds).  (default=`5')
      --profile=INT             Select one of several predefined profiles.
  -K, --keysize=STRING          Length of memcached keys (distribution).
                                  (default=`30')
      --keyorder=STRING         Selection of memcached keys to use
                                  (distribution).  (default=`none')
  -V, --valuesize=STRING        Length of memcached values (distribution).
                                  (default=`200')
  -r, --records=INT             Number of memcached records to use.  If
                                  multiple memcached servers are given, this
                                  number is divided by the number of servers.
                                  (default=`10000')
  -u, --update=FLOAT            Ratio of set:get commands.  (default=`0.0')

Advanced options:
  -U, --username=STRING         Username to use for SASL authentication.
  -P, --password=STRING         Password to use for SASL authentication.
  -T, --threads=INT             Number of threads to spawn.  (default=`1')
      --affinity                Set CPU affinity for threads, round-robin
  -c, --connections=INT         Connections to establish per server.
                                  (default=`1')
  -d, --depth=INT               Maximum depth to pipeline requests.
                                  (default=`1')
  -R, --roundrobin              Assign threads to servers in round-robin
                                  fashion.  By default, each thread connects to
                                  every server.
  -i, --iadist=STRING           Inter-arrival distribution (distribution).
                                  Note: The distribution will automatically be
                                  adjusted to match the QPS given by --qps.
                                  (default=`exponential')
  -S, --skip                    Skip transmissions if previous requests are
                                  late.  This harms the long-term QPS average,
                                  but reduces spikes in QPS after long latency
                                  requests.
      --moderate                Enforce a minimum delay of ~1/lambda between
                                  requests.
      --noload                  Skip database loading.
      --loadonly                Load database and then exit.
  -B, --blocking                Use blocking epoll().  May increase latency.
      --no_nodelay              Don't use TCP_NODELAY.
  -w, --warmup=INT              Warmup time before starting measurement.
  -W, --wait=INT                Time to wait after startup to start
                                  measurement.
      --save=STRING             Record latency samples to given file.
      --search=N:X              Search for the QPS where N-order statistic <
                                  Xus.  (i.e. --search 95:1000 means find the
                                  QPS where 95% of requests are faster than
                                  1000us).
      --scan=min:max:step       Scan latency across QPS rates from min to max.
  -e, --trace                   To enable server tracing based on client
                                  activity, will issue special
                                  start_trace/stop_trace commands. Requires
                                  memcached to support these commands.
  -G, --getq_size=INT           Size of queue for multiget requests.
                                  (default=`100')
  -g, --getq_freq=FLOAT         Frequency of multiget requests, 0 for no
                                  multi-get, 100 for only multi-get.
                                  (default=`0.0')
      --keycache_capacity=INT   Cached key capacity. (default 10000)
                                  (default=`10000')
      --keycache_reuse=INT      Number of times to reuse key cache before
                                  generating new req sequence. (Default 100)
                                  (default=`100')
      --keycache_regen=INT      When regenerating control number of requests to
                                  regenerate. (Default 1%)  (default=`1')
      --plot_all                Create plot/csv of latency histogram at each
                                  step when using gnuplot and loghistogram
                                  sampler

Agent-mode options:
  -A, --agentmode               Run client in agent mode.
  -a, --agent=host[@agent_port] Enlist remote agent, with optional agent port
                                  to support multiple agents per host.
  -p, --agent_port=STRING       Agent port, ignored when it is part of the
                                  agent option  (default=`5556')
  -l, --lambda_mul=INT          Lambda multiplier.  Increases share of QPS for
                                  this client.  (default=`1')
  -C, --measure_connections=INT Master client connections per server, overrides
                                  --connections.
  -Q, --measure_qps=INT         Explicitly set master client QPS, spread across
                                  threads and connections.
  -D, --measure_depth=INT       Set master client connection depth.
  -m, --poll_freq=INT           Set frequency in seconds for agent protocol
                                  recv polling.  (default=`1')
  -M, --poll_max=INT            Set timeout for agent protocol recv polling. An
                                  agent not responding within time limit will
                                  be dropped.  (default=`120')

The --measure_* options aid in taking latency measurements of the
memcached server without incurring significant client-side queuing
delay.  --measure_connections allows the master to override the
--connections option.  --measure_depth allows the master to operate as
an "open-loop" client while other agents continue as a regular
closed-loop clients.  --measure_qps lets you modulate the QPS the
master queries at independent of other clients.  This theoretically
normalizes the baseline queuing delay you expect to see across a wide
range of --qps values.

Predefined profiles to approximate some use cases:
1. memcached for web serving benchmark : p95, 20ms, FB key/value/IA, >4000
connections to the device under test.
2. memcached for applications backends : p99, 10ms, 32B key , 1000B value,
uniform IA,  >1000 connections
3. memcached for low latency (e.g. stock trading): p99.9, 32B key, 200B value,
uniform IA, QPS rate set to 100000	
4. P99.9, 1 msec. Key size = 32 bytes; value size has uniform distribution from
100 bytes to 1k; 

Some options take a 'distribution' as an argument.
Distributions are specified by <distribution>[:<param1>[,...]].
Parameters are not required.  The following distributions are supported:

   [fixed:]<value>              Always generates <value>.
   uniform:<max>                Uniform distribution between 0 and <max>.
   normal:<mean>,<sd>           Normal distribution.
   exponential:<lambda>         Exponential distribution.
   pareto:<loc>,<scale>,<shape> Generalized Pareto distribution.
   gev:<loc>,<scale>,<shape>    Generalized Extreme Value distribution.

   To recreate the Facebook "ETC" request stream from [1], the
   following hard-coded distributions are also provided:

   fb_value   = a hard-coded discrete and GPareto PDF of value sizes
   fb_key     = "gev:30.7984,8.20449,0.078688", key-size distribution
   fb_ia      = "pareto:0.0,16.0292,0.154971", inter-arrival time dist.

[1] Berk Atikoglu et al., Workload Analysis of a Large-Scale Key-Value Store,
    SIGMETRICS 2012
```