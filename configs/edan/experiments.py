import os
import sys

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

binaries = ["dot_product",
            "matmul",
            "mvmul",
            "prefix_sum",
            "scaled_vector_add",
            "sum",
            "vector_add"]

configs = ["--enable_caches --cpu_model=RiscvO3CPU --cpu_frequency=3.2GHz --binary="]

for binary in binaries:
    for config in configs:
        cmd = gem5_path + " " + script_path + " " + config + binaries_path + binary
        print(cmd)
        os.system(cmd)
