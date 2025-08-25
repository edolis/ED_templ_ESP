import os
import subprocess
import sys

# Inject CMake and Ninja paths
toolchain_path = r"D:\.platformio\packages\toolchain-xtensa-esp32\bin"
cmake_path = r"C:\Program Files\CMake\bin"
ninja_path = r"C:\Program Files\ninja"
os.environ["PATH"] = toolchain_path + ";" +  ninja_path + ";" + cmake_path + ";" + os.environ["PATH"]

# Debug: print PATH
print("PATH seen by idf.py:")
print(os.environ["PATH"])

# Path to idf.py
idf_py = r"D:\.platformio\packages\framework-espidf\tools\idf.py"

# Forward arguments
args = [sys.executable, idf_py] + sys.argv[1:]

# Run idf.py with patched environment
subprocess.run(args)
