import os
import sys
import subprocess

thispath = os.path.dirname(os.path.realpath(__file__))
gem5_path = os.path.join(
    thispath,
    "../../",
    "build/RISCV/gem5.opt"
)

script_path = os.path.join(
    thispath,
    "run-riscv-sim-caches.py"
)

binaries_path = os.path.join(
    thispath,
    "simple_kernels/"
)

binaries = ["matmul",
            "sum",
            "gemm"]

dram_latencies = ["10", "15", "20", "25", "30", "35", "40", "45", "50"]
cpus = ["RiscvO3CPU", "RiscvTimingSimpleCPU"]

for binary in binaries:
    for cpu in cpus:
        for latency in dram_latencies:
            with open(binaries_path + "/" + binary + "_" + latency + ".log", "w") as log:
                cmd = [gem5_path, script_path,
                       "--enable_caches",
                       "--cpu_model", cpu, "--cpu_frequency", "1GHz",
                       "--binary", binaries_path + binary,
                       "--dram_latency", latency + "ns"]
                subprocess.call(cmd, stdout=log, stderr=log)
            with open(binaries_path + "/" + binary + "_" + latency + ".log", "r") as log:
                line = log.readlines()[-2]
                time = int(line.split(" ")[1].split("=")[1])
                print(binary, cpu, latency, time)
