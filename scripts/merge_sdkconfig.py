import os
import configparser
import shlex

def merge_sdkconfig_fragments(env_override=None):
    try:
        from SCons.Script import Import
        Import("env")
    except ImportError:
        print("[DEBUG] Running outside PlatformIO. Mocking 'env'.")
        env = {"PIOENV": "main_BT"}
    else:
        env = globals().get("env", {})

    if env_override:
        env["PIOENV"] = env_override

    SDKCONFIG_DIR = "sdkconfigs"
    OUTPUT_FILE = "sdkconfig.defaults"

    active_env = env["PIOENV"]
    print(f"[merge_sdkconfig PRE] Active environment: {active_env}")

    target_file = f"sdkconfig.{active_env}"
    print(f"[merge_sdkconfig PRE] target file to replace: {target_file}")
    if os.path.exists(target_file):
        try:
            os.remove(target_file)
            print(f"[merge_sdkconfig PRE] Deleted existing fragment: {target_file}")
        except Exception as e:
            print(f"[merge_sdkconfig PRE] ERROR deleting {target_file}: {e}")

    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str
    config.read("platformio.ini")

    def get_build_flags(env_name):
        flags = []

        def extract_flags(section):
            if not config.has_option(section, "build_flags"):
                print(f"[merge_sdkconfig PRE] No build_flags in section [{section}]")
                return

            raw = config.get(section, "build_flags", fallback="")
            lines = raw.splitlines()

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                parts = shlex.split(line)
                for part in parts:
                    define = part[2:].strip() if part.startswith("-D") else part
                    if define:
                        flags.append(define)

        extract_flags("env")
        extract_flags(f"env:{env_name}")

        seen = set()
        return [f for f in flags if f not in seen and not seen.add(f)]

    flag_to_fragment = {
        "BT_ENABLED": os.path.join(SDKCONFIG_DIR, "sdkconfig.BT.defaults"),
        "FLASH4MB": os.path.join(SDKCONFIG_DIR, "sdkconfig.FLASH4MB.defaults"),
        "OPTIM_TSL": os.path.join(SDKCONFIG_DIR, "sdkconfig.OPTIM_TSL.defaults"),
        "DEBUG_BUILD": os.path.join(SDKCONFIG_DIR, "sdkconfig.DEBUG_MODE.defaults"),
        "OTA_ENABLED": os.path.join(SDKCONFIG_DIR, "sdkconfig.OTA_ENABLED.defaults"),
    }

    build_flags = get_build_flags(active_env)

    fragments = [os.path.join(SDKCONFIG_DIR, "sdkconfig.base.defaults")]

    for flag in build_flags:
        frag = flag_to_fragment.get(flag)
        if frag:
            fragments.append(frag)

    with open(OUTPUT_FILE, "w") as merged:
        for frag in fragments:
            if os.path.exists(frag):
                print(f"[merge_sdkconfig PRE] Merging fragment: {frag}")
                with open(frag, "r") as f:
                    merged.write(f.read() + "\n")
            else:
                print(f"[merge_sdkconfig PRE] WARNING: Fragment file not found: {frag}")

# 🔥 Make it directly executable
if __name__ == "__main__":
    merge_sdkconfig_fragments()
