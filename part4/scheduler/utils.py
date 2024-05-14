from enum import Enum
from typing import List, Union
import psutil


class Job(Enum):
    SCHEDULER = "scheduler"
    MEMCACHED = "memcached"
    BLACKSCHOLES = "blackscholes"
    CANNEAL = "canneal"
    DEDUP = "dedup"
    FERRET = "ferret"
    FREQMINE = "freqmine"
    RADIX = "radix"
    VIPS = "vips"


JobToImage = {
    Job.BLACKSCHOLES: "anakli/cca:parsec_blackscholes",
    Job.CANNEAL: "anakli/cca:parsec_canneal",
    Job.DEDUP: "anakli/cca:parsec_dedup",
    Job.FERRET: "anakli/cca:parsec_ferret",
    Job.FREQMINE: "anakli/cca:parsec_freqmine",
    Job.RADIX: "anakli/cca:splash2x_radix",
    Job.VIPS: "anakli/cca:parsec_vips",
}


def get_system_cpu_usage(interval=1, percpu=True) -> Union[List[float], float]:
    """
    Gets system CPU usage per available core (0 - 100%).
    For details, check documentation: https://psutil.readthedocs.io/en/latest/#psutil.cpu_percent
    :return: CPU usage (0 - 100%) per core
    """
    return psutil.cpu_percent(interval=interval, percpu=percpu)
