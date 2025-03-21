import docker
from scheduler_logger import *
from utils import *
from typing import List, Optional
import subprocess
from time import sleep
from datetime import datetime


class Controller:
    def __init__(
        self,
        init_memcached_cores: Optional[List[str]] = None,
        init_memcached_threads: int = 2,
    ):
        if init_memcached_cores is None:
            init_memcached_cores = ["0", "1"]
        self.docker_client = docker.from_env()
        self.logger = SchedulerLogger()
        self._containers = {}
        self._memcached_pid = None
        self._memcached_num_cores = len(init_memcached_cores)
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
        
        job_threads = {Job.BLACKSCHOLES: 2, Job.DEDUP: 1, Job.VIPS: 1, Job.RADIX: 2, Job.CANNEAL: 4, Job.FERRET: 2, Job.FREQMINE: 2}
        jobsA = [Job.DEDUP, Job.VIPS, Job.RADIX]
        jobsB = [Job.BLACKSCHOLES, Job.CANNEAL, Job.FERRET, Job.FREQMINE]
        
        get_system_cpu_usage()
        memcached_proc = psutil.Process(self._memcached_pid)
        memcached_proc.cpu_percent()
        
        memcached_cores_prev = self._memcached_num_cores
        memcached_cores = self._memcached_num_cores
        
        active_jobA_id, active_jobB_id = 0, 0
        self._job_start(jobsA[active_jobA_id], ["1"], job_threads[jobsA[active_jobA_id]])
        self._job_pause(jobsA[active_jobA_id])
        self._job_start(jobsB[active_jobB_id], ["2", "3"], job_threads[jobsB[active_jobB_id]])
        
        start=datetime.now()
        i = 0
        elapsed_time = 1.25
        while True:
            mc_cpu_usage = memcached_proc.cpu_percent()
            total_cpu_usage = get_system_cpu_usage()
            i += 1
            if i == 10:
                print(f"Memcached CPU usage: {mc_cpu_usage}%")
                print(f"Memcached cores: {memcached_cores}")
                print(f"Total CPU usage: {total_cpu_usage}%")
                print(f"Elapsed time: {datetime.now()-start}s")
                print(f'Remaining Jobs:\n{jobsA[active_jobA_id:]}\n{jobsB[active_jobB_id:]}')
                print()
                i = 0
            
            if elapsed_time > 1:
                self._adjust_memcached_cores(mc_cpu_usage)
                elapsed_time = 0
                
            jobsA_done = (active_jobA_id == len(jobsA))
            jobsB_done = (active_jobB_id == len(jobsB))
            jobsB_cores = ["1", "2", "3"] if jobsA_done else ["2", "3"]
            jobsA_cores = ["1", "2", "3"] if jobsB_done else ["1"]
            
            if jobsA_done and jobsB_done:
                break 
           
            memcached_cores = self._memcached_num_cores
            if memcached_cores_prev == 2 and memcached_cores == 1: 
                if jobsB_done:
                    self._update_cores(jobsA[active_jobA_id], ["1", "2", "3"])
                    print(f"Updating cores of job {jobsA[active_jobA_id].value} to {[1, 2, 3]}...")
                elif jobsA_done:
                    self._update_cores(jobsB[active_jobB_id], ["1", "2", "3"])
                    print(f"Updating cores of job {jobsB[active_jobB_id].value} to {[1, 2, 3]}...")
                else:
                    self._job_unpause(jobsA[active_jobA_id])
                    print(f"Unpausing job {jobsA[active_jobA_id].value}...")
            if memcached_cores_prev == 1 and memcached_cores == 2:
                if jobsB_done:
                    self._update_cores(jobsA[active_jobA_id], ["2", "3"])
                    print(f"Updating cores of job {jobsA[active_jobA_id].value} to {[2, 3]}...")
                elif jobsA_done:
                    self._update_cores(jobsB[active_jobB_id], ["2", "3"])
                    print(f"Updating cores of job {jobsB[active_jobB_id].value} to {[2, 3]}...")
                else:
                    self._job_pause(jobsA[active_jobA_id])  
                    print(f"Pausing job {jobsA[active_jobA_id].value}...")
            memcached_cores_prev = memcached_cores 
            
            if active_jobA_id < len(jobsA):
                if self._job_status(jobsA[active_jobA_id]) == "exited":
                    self._job_end(jobsA[active_jobA_id])
                    active_jobA_id += 1
                    if active_jobA_id < len(jobsA):
                        self._job_start(jobsA[active_jobA_id], jobsA_cores, job_threads[jobsA[active_jobA_id]])
                    else:
                        if active_jobB_id < len(jobsB):
                            jobsB_cores = ["1", "2", "3"] if self._memcached_num_cores == 1 else ["2", "3"]
                            self._update_cores(jobsB[active_jobB_id], jobsB_cores)
                            if self._job_status(jobsB[active_jobB_id]) == "paused":
                                self._job_unpause(jobsB[active_jobB_id])
                            print(f"Updating cores of job {jobsB[active_jobB_id].value} to {jobsB_cores}...")
                            print(f"Unpausing job {jobsB[active_jobB_id].value}...")

            if active_jobB_id < len(jobsB):
                if self._job_status(jobsB[active_jobB_id]) == "exited":
                    self._job_end(jobsB[active_jobB_id])
                    active_jobB_id += 1
                    if active_jobB_id < len(jobsB):
                        self._job_start(jobsB[active_jobB_id], jobsB_cores, job_threads[jobsB[active_jobB_id]])   
                    else:
                        if active_jobA_id < len(jobsA):
                            jobsA_cores = ["1", "2", "3"] if self._memcached_num_cores == 1 else ["2", "3"]
                            self._update_cores(jobsA[active_jobA_id], jobsB_cores)
                            if self._job_status(jobsA[active_jobA_id]) == "paused":
                                self._job_unpause(jobsA[active_jobA_id])
                            print(f"Unpausing job {jobsA[active_jobA_id].value}...")
                            print(f"Updating cores of job {jobsA[active_jobA_id].value} to {jobsA_cores}...")
                        
            sleep(0.25)
            elapsed_time += 0.25

        self._set_memcached_cores(["0", "1"])
        if not self._end():
            raise Exception("Error when shutting down scheduler.")

    def _adjust_memcached_cores(self, mc_cpu_usage: float) -> None:
        if self._memcached_num_cores == 1 and mc_cpu_usage >= 34.68:
            self._set_memcached_cores(["0", "1"])
        elif self._memcached_num_cores == 2 and mc_cpu_usage < 45:
            self._set_memcached_cores(["0"])

    def _set_memcached_cores(self, cores: List[str]) -> bool:
        print(f"Setting Memcached CPUs to {cores}")
        cpus = ",".join(cores)
        command = f"sudo taskset -a -cp {cpus} {self._memcached_pid}"
        subprocess.run(
            command.split(" "), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
        )
        self._memcached_num_cores = len(cores)
        self.logger.update_cores(Job.MEMCACHED, cores)
        return True

    def _job_start(
        self, job: Job, initial_cores: list[str], initial_threads: int
    ) -> bool:
        assert job != Job.SCHEDULER, "You cannot start job scheduler!"

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
        
        self.logger.job_start(
            job=job, initial_cores=initial_cores, initial_threads=initial_threads
        )
        return True

    def _job_status(self, job: Job) -> str:
        assert job != Job.SCHEDULER, "You cannot check job scheduler!"
        if self._containers.get(job) is None:
            print(f"No associated container found with job {job.value}.")
            return "job not found"
        self._containers.get(job).reload()
        return self._containers.get(job).status
    
    def _job_end(self, job: Job) -> bool:
        if self._job_status(job) != "exited":
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
        self._containers.get(job).update(cpuset_cpus=",".join(cores))
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
        self.logger.job_unpause(job=job)
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
        self._containers.clear()
        self.logger.end()
        return True
    

if __name__ == "__main__":
    controller = Controller()
    controller.run_scheduler()
