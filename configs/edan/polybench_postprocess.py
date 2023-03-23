import os
import sys

thispath = os.path.dirname(os.path.realpath(__file__))
binary_dir = thispath + "/kernels/"


def process_sim_time():
    niters = int(sys.argv[1])
    for subdir, dirs, files in os.walk(binary_dir):
        for file in files:
            if ".log" not in file: # found a binary
                avg_time = 0.0
                binary_name = os.path.join(subdir, file)

                for i in range(niters):
                    with open(binary_name + "." + str(i) + ".log", "r") as log:
                        for line in log:
                            pass

                        last_line = line
                        avg_time = avg_time + float(line.split(" ")[1].split("=")[1])

                avg_time = avg_time / niters
                print(file, avg_time)


def process_dram_latency_impact():
    blacklist = ["adi", "fdtd-2d",  "fdtd-apml",
                 "jacobi-1d-imper", "jacobi-2d-imper", "seidel-2d",
                 "correlation", "covariance", "floyd-warshall", "reg_detect"]
    dram_latencies = ["10", "15", "20", "25", "30", "35", "40", "45", "50"]
    cpus = ["RiscvO3CPU", "RiscvTimingSimpleCPU"]

    for subdir, dirs, files in os.walk(binary_dir):
        for file in files:
            if (file in blacklist) or ".log" in file:
                continue

            binary_name = os.path.join(subdir, file)
            
            for cpu in cpus:
                for latency in dram_latencies:
                    with open(binary_name + ".dram_lat." + latency + ".log", "r") as log:
                        line = log.readlines()[-2]
                        time = int(line.split(" ")[1].split("=")[1])
                        print(file, cpu, latency, time)

#process_sim_time():
#process_dram_latency_impact()
