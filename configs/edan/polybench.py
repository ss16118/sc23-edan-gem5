import sys
import os
import subprocess
from pathlib import Path

dataset_type = sys.argv[1]
niters = int(sys.argv[2])

# cross-compile polybench for riscv

thispath = os.path.dirname(os.path.realpath(__file__))
polybench_root = thispath + "/polybench-c-3.2/"
binary_dir = thispath + "/kernels/"

if not Path(binary_dir).is_dir():
    os.mkdir(binary_dir)

for subdir, dirs, files in os.walk(polybench_root):
    if "utilities" in subdir:
        continue

    for file in files:
        if ".h" in file:
            continue
        
        cmd = "riscv64-unknown-linux-gnu-gcc -static -O3 " + \
            " -I " + polybench_root + "/utilities/ " + \
            polybench_root + "/utilities/polybench.c " + \
            os.path.join(subdir, file) + \
            " -D" + dataset_type + \
            " -o " + binary_dir + file[:-2] + \
            " -lm "

        print(cmd)
        os.system(cmd)

# run gem5 experiments

gem5_path = os.path.join(
    thispath,
    "../../",
    "build/RISCV/gem5.opt"
)

script_path = os.path.join(
    thispath,
    "run-riscv-sim-caches.py"
)


def measure_sim_time():
    for subdir, dirs, files in os.walk(binary_dir):
        for file in files:
            binary_name = os.path.join(subdir, file)
            for i in range(niters):
                with open(binary_name + "." + str(i) + ".log", "w") as log:
                    cmd = [gem5_path, script_path,
                           "--binary", binary_name,
                           "--cpu_model", "RiscvO3CPU",
                           "--cpu_frequency", "1GHz",
                           "--enable_caches"]               

                    print(binary_name, i)
                    subprocess.call(cmd, stdout=log, stderr=log)


def measure_dram_latency_impact():
    blacklist = ["adi", "fdtd-2d",  "fdtd-apml",
                 "jacobi-1d-imper", "jacobi-2d-imper", "seidel-2d",
                 "correlation", "covariance", "floyd-warshall", "reg_detect"]
#    dram_latencies = ["10", "15", "20", "25", "30", "35", "40", "45", "50"]
    dram_latencies = ["55", "60", "65", "70", "75", "80", "85", "90", "95",
                      "100", "105", "110", "115", "120", "125", "130", "135", "140", "145", "150",
                      "155", "160", "165", "170", "175", "180", "185", "190", "195", "200"]
    cpus = ["RiscvO3CPU", "RiscvTimingSimpleCPU"]

    for subdir, dirs, files in os.walk(binary_dir):
        for file in files:
            if file in blacklist:
                continue

            binary_name = os.path.join(subdir, file)

            for cpu in cpus:
                for latency in dram_latencies:
                    with open(binary_name + ".dram_lat." + latency + ".log", "w") as log:
                        cmd = [gem5_path, script_path,
                               "--enable_caches",
                               "--cpu_model", cpu, "--cpu_frequency", "1GHz",
                               "--binary", binary_name,
                               "--dram_latency", latency + "ns"]

                        print(binary_name, cpu, latency)
                        subprocess.call(cmd, stdout=log, stderr=log)

#measure_sim_time()
measure_dram_latency_impact()
