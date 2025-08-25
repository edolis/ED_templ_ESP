Import("env")
import merge_sdkconfig
import update_version_comment

print("[extra_script] Loaded successfully")
print("[prebuild] Starting pre-build sequence...")

# Just call your functions directly — no need for AddPreAction
merge_sdkconfig.merge_sdkconfig_fragments(env.get("PIOENV"))
update_version_comment.update_version_comment()

print("[prebuild] ✅ Pre-build sequence completed.")
