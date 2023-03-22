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

gem5_config = "--binary"

for subdir, dirs, files in os.walk(binary_dir):
    for file in files:
        binary_name = os.path.join(subdir, file)
        for i in range(niters):
            with open(binary_name + "." + str(i) + ".log", "w") as log:
                cmd = [gem5_path, script_path,
                       gem5_config, binary_name,
                       "--cpu_model", "RiscvO3CPU",
                       "--cpu_frequency", "1GHz",
                       "--enable_caches"]               
                print(cmd[1])
                subprocess.call(cmd, stdout=log)
