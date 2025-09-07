import configparser
import shlex
import subprocess
import os

def get_app_name(env_name, ini_path="platformio.ini"):
    config = configparser.ConfigParser()
    config.read(ini_path)

    flags = []

    def extract_flags(section):
        if not config.has_option(section, "build_flags"):
            return
        raw = config.get(section, "build_flags", fallback="")
        lines = raw.splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith(";"):
                continue
            parts = shlex.split(line)
            for part in parts:
                if part.startswith("-DAPP_NAME="):
                    value = part.split("=", 1)[1].strip('"')
                    flags.append(value)

    extract_flags("env")
    extract_flags(f"env:{env_name}")

    return flags[0] if flags else "default_1_app"

def get_git_version():
    try:
        return subprocess.check_output(
            ["git", "describe", "--tags", "--dirty", "--always"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "v0.0.0-0-unknown"

def inject(env=None):
    print("[inject_app_metadata] started")

    # Determine environment name
    env_name = env.get("PIOENV") if env else os.environ.get("PIOENV", "esp32")

    # Extract values
    app_name = get_app_name(env_name)
    git_version = get_git_version()
    #full_version = f"{app_name}_{git_version}"
    full_version = f"{git_version}"

    print(f"[inject_app_metadata] injecting metadata: {full_version}")

    if env:
        # Inject into CMake via build system
        env.Replace(CMAKE_EXTRA_ARGS=[
            f"-DPROJECT_NAME={app_name}",
            f"-DPROJECT_VER={full_version}"
        ])

        # Also set environment variables for CMake to read via $ENV{}
        env["ENV"]["PROJECT_NAME"] = app_name
        env["ENV"]["PROJECT_VER"] = full_version
    else:
        # Standalone mode
        print(f"[inject_app_metadata] PROJECT_NAME={app_name}")
        print(f"[inject_app_metadata] PROJECT_VER={full_version}")

# If run as standalone script
if __name__ == "__main__":
    inject()
