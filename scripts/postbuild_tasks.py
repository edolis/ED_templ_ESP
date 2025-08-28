Import("env")
import os
from process_sizeInfo import show_size_and_pct

def run_all_post_build_actions(source, target, env):
    elf_path = target[0].get_abspath()
    show_size_and_pct(env, elf_path)

# ✅ This ensures your function runs *after* the ELF is built
env.AddPostAction("$BUILD_DIR/${PROGNAME}.elf", run_all_post_build_actions)
