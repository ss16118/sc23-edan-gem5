import os
import sys

niters = int(sys.argv[1])

thispath = os.path.dirname(os.path.realpath(__file__))
binary_dir = thispath + "/kernels/"

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
