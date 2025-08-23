import os
import configparser
import shlex
try:
    from SCons.Script import Import
    Import("env")
except ImportError:
    print("[DEBUG] Running outside PlatformIO. Mocking 'env'.")
    env = {"PIOENV": "main_BT"}  # or whatever env you want to test

#patch for secrets.h

# env.Append(CPPPATH=["include"])
# env.Append(CPPPATH=["./include"])

# # Add include path for libraries
# for item in env.get("LIBS", []):
#     env.Append(CPPPATH=["../../include"])

# Import("env")

# Constants
SDKCONFIG_DIR = "sdkconfigs"
OUTPUT_FILE = "sdkconfig.defaults"

# Get active environment name from PlatformIO context
active_env = env["PIOENV"]
# active_env="main_BT"

print(f"[merge_sdkconfig PRE] Active environment: {active_env}")

target_file = "sdkconfig."+active_env
print(f"[merge_sdkconfig PRE] target file to replace: {target_file}")
if os.path.exists(target_file):
    try:
        os.remove(target_file)
        print(
            f"[merge_sdkconfig PRE] Deleted existing fragment: {target_file}")
    except Exception as e:
        print(f"[merge_sdkconfig PRE] ERROR deleting {target_file}: {e}")

# Parse platformio.ini
config = configparser.ConfigParser(allow_no_value=True)
config.optionxform = str  # preserve case
config.read("platformio.ini")

# Collect build_flags from both [env] and [env:active_env]


def get_build_flags(env_name):
    flags = []

    def extract_flags(section):
       # print(f"[merge_sdkconfig PRE] Processing section: [{section}]")
        if not config.has_option(section, "build_flags"):
            print(
                f"[merge_sdkconfig PRE] No build_flags in section [{section}]")
            return

        raw = config.get(section, "build_flags", fallback="")
        lines = raw.splitlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Split line into parts using shell-like syntax
            parts = shlex.split(line)
            for part in parts:
                define = part[2:].strip() if part.startswith("-D") else part
                if define:
                    #print(
                    #    f"[merge_sdkconfig PRE] Found flag: '{define}' in section [{section}]")
                    flags.append(define)

    extract_flags("env")
    extract_flags(f"env:{env_name}")

    # Remove duplicates while preserving order
    seen = set()
    return [f for f in flags if f not in seen and not seen.add(f)]


# Map flags to sdkconfig fragments
flag_to_fragment = {
    "BT_ENABLED": os.path.join(SDKCONFIG_DIR, "sdkconfig.BT.defaults"),
    "FLASH4MB": os.path.join(SDKCONFIG_DIR, "sdkconfig.FLASH4MB.defaults"),
    "OPTIM_TSL": os.path.join(SDKCONFIG_DIR, "sdkconfig.OPTIM_TSL.defaults"),
    "DEBUG_MODE": os.path.join(SDKCONFIG_DIR, "sdkconfig.DEBUG_MODE.defaults")
}

# Get flags
build_flags = get_build_flags(active_env)
#print(f"[merge_sdkconfig PRE] Combined build_flags: {build_flags}")

# Start with base fragment
fragments = [os.path.join(SDKCONFIG_DIR, "sdkconfig.base.defaults")]
#print("[merge_sdkconfig PRE] Base fragment added.")

# Match flags to fragments
for flag in build_flags:
    frag = flag_to_fragment.get(flag)
    if frag:
        #print(
        #    f"[merge_sdkconfig PRE] Flag '{flag}' matched to fragment '{frag}'")
        fragments.append(frag)
    #else:
    #    print(
    #        f"[merge_sdkconfig PRE] Flag '{flag}' not mapped to any fragment.")

# Merge fragments
with open(OUTPUT_FILE, "w") as merged:
    for frag in fragments:
        if os.path.exists(frag):
            print(f"[merge_sdkconfig PRE] Merging fragment: {frag}")
            with open(frag, "r") as f:
                merged.write(f.read() + "\n")
        else:
            print(
                f"[merge_sdkconfig PRE] WARNING: Fragment file not found: {frag}")
