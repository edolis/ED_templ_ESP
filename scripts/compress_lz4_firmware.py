import os
import shutil
import subprocess
import time
import lz4.block  # ✅ still using block API

def get_git_version():
    try:
        return subprocess.check_output(
            ["git", "describe", "--tags", "--dirty", "--always"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "v0.0.0-0-unknown"

def wait_for_firmware(firmware_path, timeout=5):
    for _ in range(timeout * 10):  # check every 0.1s
        if os.path.isfile(firmware_path):
            return True
        time.sleep(0.1)
    return False

def compress_and_archive_firmware(env, elf_path=None):
    print("[compress_firmware] Starting compression and archiving...")

    build_dir = os.path.dirname(elf_path) if elf_path else env["BUILD_DIR"]
    firmware_path = os.path.join(build_dir, "firmware.bin")

    if not wait_for_firmware(firmware_path):
        print(f"[compress_firmware] ❌ Firmware not found: {firmware_path}")
        print(f"[debug] Files in build dir: {os.listdir(build_dir)}")
        return

    app_name = env["ENV"].get("PROJECT_NAME", "default_app")
    project_ver = env["ENV"].get("PROJECT_VER", get_git_version())
    full_version = f"{app_name}_{project_ver}"
    file_name = f"{full_version}.bin.lz4"

    target_dir = r"\\raspi00\fware"
    archive_dir = os.path.join(target_dir, "obs")
    os.makedirs(archive_dir, exist_ok=True)

    # Archive old firmware files
    for fname in os.listdir(target_dir):
        if fname.startswith(app_name) and fname.endswith(".bin.lz4"):
            try:
                # shutil.move(os.path.join(target_dir, fname), os.path.join(archive_dir, fname))
                print(f"[compress_firmware] Archived: {fname}")
            except Exception as e:
                print(f"[compress_firmware] Failed to archive {fname}: {e}")

    compressed_path = os.path.join(target_dir, file_name)

    try:
        chunk_size = 4096
        total_chunks = 0
        total_original = 0
        total_compressed = 0

        history = b""  # rolling dictionary buffer

        with open(firmware_path, "rb") as f_in, open(compressed_path, "wb") as f_out:
            while True:
                chunk = f_in.read(chunk_size)
                if not chunk:
                    break

                compressed_chunk = lz4.block.compress(
                    chunk,
                    mode='high_compression',
                    store_size=False,
                    compression=9,
                    dict=history
                )

                total_chunks += 1
                total_original += len(chunk)
                total_compressed += len(compressed_chunk)

                size_bytes = len(compressed_chunk).to_bytes(4, byteorder='little')

                # if total_chunks <= 3:
                    # print(f"[debug] Chunk {total_chunks}: {len(chunk)} -> {len(compressed_chunk)} bytes")
                    # print(f"[debug] Size header bytes: {' '.join(f'{b:02x}' for b in size_bytes)}")
                    # print(f"[debug] First 8 bytes of compressed: {' '.join(f'{b:02x}' for b in compressed_chunk[:8])}")

                f_out.write(size_bytes)
                f_out.write(compressed_chunk)

                # Update rolling dictionary (max 16KB)
                DICT_SIZE = 16 * 1024  # 16 KB dictionary to match ESP32
                history = (history + chunk)[-DICT_SIZE:]


        # Verification
        # print(f"[debug] Verifying compressed file structure...")
        # with open(compressed_path, "rb") as f_verify:
        #     for i in range(min(3, total_chunks)):
        #         size_header = f_verify.read(4)
        #         if len(size_header) != 4:
        #             break
        #         size = int.from_bytes(size_header, byteorder='little')
        #         compressed_data = f_verify.read(size)
        #         print(f"[debug] Verification chunk {i+1}: size_header={' '.join(f'{b:02x}' for b in size_header)}, size={size}, got {len(compressed_data)} bytes")
        #         print(f"[debug] First 8 bytes of data: {' '.join(f'{b:02x}' for b in compressed_data[:8])}")

        print(f"[compress_firmware] ✅ Saved: {compressed_path}")
        print(f"[compress_firmware] Total chunks: {total_chunks}")
        print(f"[compress_firmware] Original size: {total_original} bytes")
        print(f"[compress_firmware] Compressed size: {total_compressed} bytes (ratio: {total_compressed/total_original:.2f})")

    except Exception as e:
        print(f"[compress_firmware] ❌ Compression failed: {e}")
