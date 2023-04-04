import os
import sys

thispath = os.path.dirname(os.path.realpath(__file__))
binary_dir = thispath + "/kernels.l1_only/"


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

def process_dram_latency_impact_slowdown():
    blacklist = ["adi", "fdtd-2d",  "fdtd-apml",
                 "jacobi-1d-imper", "jacobi-2d-imper", "seidel-2d",
                 "correlation", "covariance", "floyd-warshall", "reg_detect",
                 "dynprog", "lu", "ludcmp", "gramschmidt", "durbin"]
    dram_latencies = ["10", "15", "20", "25", "30", "35", "40", "45", "50",
                      "55", "60", "65", "70", "75", "80", "85", "90", "95", "100",
                      "105", "110", "115", "120", "125", "130", "135", "140", "145", "150",
                      "155", "160", "165", "170", "175", "180", "185", "190", "195", "200",
                      "205", "210", "215", "220", "225", "230", "235", "240", "245", "250",
                      "255", "260", "265", "270", "275", "280", "285", "290", "295", "300"]
                      
    cpus = ["RiscvO3CPU"]

    for subdir, dirs, files in os.walk(binary_dir):
        for file in files:
            if (file in blacklist) or ".log" in file:
                continue

            binary_name = os.path.join(subdir, file)
            
            for cpu in cpus:
                baseline = 0.0
                norm_sum = 0.0
                abs_sum = 0.0
                for latency in dram_latencies:
                    with open(binary_name + "." + cpu + ".dram_lat_l1only." + latency + ".log", "r") as log:
                        line = log.readlines()[-4]
                        time = float(line)
                        if baseline == 0:
                            baseline = time
                        norm_sum = norm_sum + time / baseline
                        abs_sum = abs_sum + time
                        #print(file, cpu, latency, time, time / baseline)
                        print(file, cpu, latency, time, time / baseline)
                print(file, cpu, "avg", abs_sum / len(dram_latencies), norm_sum / len(dram_latencies))

#process_sim_time()
#process_dram_latency_impact()
process_dram_latency_impact_slowdown()
