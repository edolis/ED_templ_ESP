import os
import shutil
import subprocess
import lz4.frame

def get_git_version():
    try:
        return subprocess.check_output(
            ["git", "describe", "--tags", "--dirty", "--always"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "v0.0.0-0-unknown"

def get_app_name(env):
    for define in env.get("CPPDEFINES", []):
        if isinstance(define, tuple) and define[0] == "APP_NAME":
            return define[1].strip('"')
        elif isinstance(define, str) and define.startswith("APP_NAME="):
            return define.split("=", 1)[1].strip('"')
    return "default_app"

def compress_and_archive_firmware(env, elf_path=None):
    print("[compress_firmware] Starting compression and archiving...")

    # Use ELF path to locate build directory
    build_dir = os.path.dirname(elf_path) if elf_path else env["BUILD_DIR"]
    firmware_path = os.path.join(build_dir, "firmware.bin")

    if not os.path.isfile(firmware_path):
        print(f"[compress_firmware] ❌ Firmware not found: {firmware_path}")
        print(f"[debug] Files in build dir: {os.listdir(build_dir)}")
        return

    # ✅ Read app_name and version from environment variables
    app_name = env["ENV"].get("PROJECT_NAME", "default_app")
    #print(f"[debug] appname is {app_name} ")
    full_version = app_name +"_"+ env["ENV"].get("PROJECT_VER", f"v0.0.0-0-unknown")

    file_name = f"{full_version}.bin.lz4"

    target_dir = r"\\raspi00\fware"
    archive_dir = os.path.join(target_dir, "obs")
    os.makedirs(archive_dir, exist_ok=True)

    # Move old firmware files
    for fname in os.listdir(target_dir):
        if fname.startswith(app_name) and fname.endswith(".bin.lz4"):
            try:
                shutil.move(os.path.join(target_dir, fname), os.path.join(archive_dir, fname))
                print(f"[compress_firmware] Archived: {fname}")
            except Exception as e:
                print(f"[compress_firmware] Failed to archive {fname}: {e}")

    # Compress firmware
    compressed_path = os.path.join(target_dir, file_name)
    try:
        with open(firmware_path, "rb") as f_in:
            with lz4.frame.open(compressed_path, "wb") as f_out:
                f_out.write(f_in.read())
        print(f"[compress_firmware] ✅ Saved: {compressed_path}")
    except Exception as e:
        print(f"[compress_firmware] ❌ Compression failed: {e}")

