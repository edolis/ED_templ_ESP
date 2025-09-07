Import("env")
import os
from process_sizeInfo import show_size_and_pct
from compress_lz4_firmware import compress_and_archive_firmware

def run_all_post_build_actions(source, target, env):
    elf_path = target[0].get_abspath()
    show_size_and_pct(env, elf_path)
    compress_and_archive_firmware(env, elf_path)

env.AddPostAction("$BUILD_DIR/${PROGNAME}.elf", run_all_post_build_actions)
