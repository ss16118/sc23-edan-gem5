# Copyright (c) 2015 Jason Power
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import time
import m5

m5.util.addToPath("../")

from caches import *
from m5.objects import *
from common import SimpleOpts


default_cpu_model = "RiscvTimingSimpleCPU"
default_cpu_frequency = "3.0GHz"
default_dram_size = "16GB"
default_dram_latency = "10ns"
default_l1d_size = "64kB"
default_l1d_latency = 4
default_l1i_size = "16kB"
default_l1i_latency = 4
default_l2_size = "256kB"
default_l2_latency = 20


def print_sim_params(params):
    print(f"EDAN: binary={params.binary}")
    print(f"EDAN: cpu_model={params.cpu_model}")
    print(f"EDAN: cpu_frequency={params.cpu_frequency}")
    print(f"EDAN: dram_size={params.dram_size}")
    print(f"EDAN: dram_latency={params.dram_latency}")

    if params.enable_caches:
        print(f"EDAN: l1i_size={params.l1i_size}")
        print(f"EDAN: l1i_latency={params.l1i_latency}cycles")
        print(f"EDAN: l1d_size={params.l1d_size}")
        print(f"EDAN: l1d_size={params.l1d_latency}cycles")
        print(f"EDAN: l2_size={params.l2_size}")
        print(f"EDAN: l2_size={params.l2_latency}cycles")
    else:
        print("EDAN: Caches disabled.")


def get_sim_params():
    SimpleOpts.add_option("--binary", nargs="?", default="")
    SimpleOpts.add_option("--cpu_model", nargs="?", default=default_cpu_model)
    SimpleOpts.add_option("--cpu_frequency", nargs="?", default=default_cpu_frequency)
    SimpleOpts.add_option("--dram_size", nargs="?", default=default_dram_size)
    SimpleOpts.add_option("--dram_latency", nargs="?", default=default_dram_latency)
    SimpleOpts.add_option("--enable_caches", action='store_true')
    SimpleOpts.add_option("--l1d_size", nargs="?", default=default_l1d_size)
    SimpleOpts.add_option("--l1d_latency", nargs="?", default=default_l1d_latency)
    SimpleOpts.add_option("--l1i_size", nargs="?", default=default_l1i_size)
    SimpleOpts.add_option("--l1i_latency", nargs="?", default=default_l1i_latency)
    SimpleOpts.add_option("--l2_size", nargs="?", default=default_l2_size)
    SimpleOpts.add_option("--l2_latency", nargs="?", default=default_l2_latency)
    
    return SimpleOpts.parse_args()


### Initialize simulation environment
def init_sim_env(params):
    system = System()

    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = params.cpu_frequency
    system.clk_domain.voltage_domain = VoltageDomain()
    system.mem_mode = "timing"
    system.mem_ranges = [AddrRange(params.dram_size)]

    if params.cpu_model == default_cpu_model:
        system.cpu = RiscvTimingSimpleCPU()
    elif params.cpu_model == "RiscvO3CPU":
        system.cpu = RiscvO3CPU()
    else:
        sys.exit("Unsupported cpu model!")

    system.membus = SystemXBar()

    if params.enable_caches:
        system.cpu.icache = L1ICache(params)
        system.cpu.dcache = L1DCache(params)
        system.cpu.icache.connectCPU(system.cpu)
        system.cpu.dcache.connectCPU(system.cpu)

        system.l2bus = L2XBar()
        system.cpu.icache.connectBus(system.l2bus)
        system.cpu.dcache.connectBus(system.l2bus)
        system.l2cache = L2Cache(params)
        system.l2cache.connectCPUSideBus(system.l2bus)
        system.l2cache.connectMemSideBus(system.membus)

    else:
        system.cpu.icache_port = system.membus.cpu_side_ports
        system.cpu.dcache_port = system.membus.cpu_side_ports

    system.cpu.createInterruptController()

    system.mem_ctrl = MemCtrl(static_frontend_latency=params.dram_latency)
    system.mem_ctrl.dram = DDR4_2400_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports
    system.system_port = system.membus.cpu_side_ports

    system.workload = SEWorkload.init_compatible(params.binary)
    process = Process()
    process.cmd = [params.binary]
    system.cpu.workload = process
    system.cpu.createThreads()

    return system


### Gem5 simulation
params = get_sim_params()
print_sim_params(params)
system = init_sim_env(params)
root = Root(full_system=False, system=system)
m5.instantiate()

print("EDAN: Beginning simulation!")

t1 = time.perf_counter()
exit_event = m5.simulate()
t2 = time.perf_counter()

print(f"EDAN: exited with {exit_event.getCause()}")
print(f"EDAN: simulated_time={m5.curTick()} cycles")
print(f"EDAN: simulation_time={t2 - t1} seconds")
