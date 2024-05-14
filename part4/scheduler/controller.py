import docker
from scheduler_logger import *
from utils import *
from typing import List, Optional
import subprocess
from time import sleep


class Controller:
    def __init__(
        self,
        init_memcached_cores: Optional[List[str]] = None,
        init_memcached_threads: int = 2,
    ):
        if init_memcached_cores is None:
            init_memcached_cores = ["0"]
        self.docker_client = docker.from_env()
        self.logger = SchedulerLogger()
        self._containers = {}
        self._memcached_pid = None
        for proc in psutil.process_iter():
            if proc.name() == "memcached":
                self._memcached_pid = proc.pid
                break
        if self._memcached_pid is None:
            raise Exception("Memcached PID not found...")
        cpus = ",".join(init_memcached_cores)
        command = f"sudo taskset -a -cp {cpus} {self._memcached_pid}"
        subprocess.run(
            command.split(" "), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
        )
        self.logger.job_start(
            Job.MEMCACHED, init_memcached_cores, init_memcached_threads
        )

    def run_scheduler(self) -> None:
        # TODO: Schedule the job execution here
        # Note, use get_system_cpu_usage() function in `utils` to track CPU percentages per core.
        # Don't change this line. The first value will be 0 so it needs to be ignored.
        get_system_cpu_usage()
        memcached_proc = psutil.Process(self._memcached_pid)
        while True:
            mc_cpu_usage = memcached_proc.cpu_percent()
            total_cpu_usage = get_system_cpu_usage()
            print(f"Memcached CPU usage: {mc_cpu_usage}%")
            print(f"Total CPU usage: {total_cpu_usage}%")
            sleep(0.25)
            break
        if not self._end():
            raise Exception("Error when shutting down scheduler.")

    def _set_memcached_cores(self, cores: List[str]) -> bool:
        print(f"Setting Memcached CPUs to {cores}")
        cpus = ",".join(cores)
        command = f"sudo taskset -a -cp {cpus} {self._memcached_pid}"
        subprocess.run(
            command.split(" "), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
        )
        self.logger.update_cores(Job.MEMCACHED, cores)
        return True

    def _job_start(
        self, job: Job, initial_cores: list[str], initial_threads: int
    ) -> bool:
        assert job != Job.SCHEDULER, "You cannot start job scheduler!"

        self.logger.job_start(
            job=job, initial_cores=initial_cores, initial_threads=initial_threads
        )
        print(f"Starting job {job.value}")
        job_type = 'parsec' if job != Job.RADIX else 'splash2x'
        container = self.docker_client.containers.run(
            image=JobToImage[job],
            command=f"./run -a run -S {job_type} -p {job.value} -i native -n {str(initial_threads)}",
            cpuset_cpus=",".join(initial_cores),
            name=job.value,
            remove=False,
            detach=True,
        )
        container.reload()
        self._containers[job] = container
        return True

    def _job_end(self, job: Job) -> bool:
        assert job != Job.SCHEDULER, "You cannot end job scheduler!"
        if self._containers.get(job) is None:
            print(f"No associated container found with job {job.value}.")
            return False
        self._containers.get(job).reload()
        if self._containers.get(job).status != "exited":
            print(f"Container for job {job.value} is still `{self._containers.get(job).status}`.")
            return False
        self.logger.job_end(job=job)
        print(f"Removing container for job: {job.value}...")
        self._containers.get(job).remove()
        self._containers.pop(job)
        return True

    def _update_cores(self, job: Job, cores: list[str]) -> bool:
        assert job != Job.SCHEDULER, "Cannot schedule cores to scheduler!"
        if self._containers.get(job) is None:
            print(f"No associated container found with job {job.value}.")
            return False
        self.logger.update_cores(job=job, cores=cores)
        self._containers.get(job).update(cpuset_cpus=cores)
        self._containers.get(job).reload()
        return True

    def _job_pause(self, job: Job) -> bool:
        assert job != Job.SCHEDULER, "Seriously?!"
        if self._containers.get(job) is None:
            print(f"No associated container found with job {job.value}.")
            return False

        self.logger.job_pause(job=job)
        self._containers.get(job).pause()
        self._containers.get(job).reload()
        return True

    def _job_unpause(self, job: Job) -> bool:
        assert job != Job.SCHEDULER, "Seriously?!"
        if self._containers.get(job) is None:
            print(f"No associated container found with job {job.value}.")
            return False
        self.logger.job_pause(job=job)
        self._containers.get(job).unpause()
        self._containers.get(job).reload()
        return True

    def _custom_event(self, job: Job, comment: str):
        self.logger.custom_event(job=job, comment=comment)
        # TODO: Placeholder if needed
        return True

    def _end(self) -> bool:
        for job in self._containers.keys():
            container = self._containers.get(job)
            self._containers.get(job).reload()
            if container.status != "exited":
                container.remove()
            self._containers.pop(job)
        self.logger.end()
        return True


if __name__ == "__main__":
    controller = Controller()
    controller.run_scheduler()
