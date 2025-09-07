Import("env")
import merge_sdkconfig
import update_version_comment
import inject_app_metadata

print("[extra_script] Loaded successfully")
print("[prebuild] Starting pre-build sequence...")

# Just call your functions directly — no need for AddPreAction
merge_sdkconfig.merge_sdkconfig_fragments(env.get("PIOENV"))
update_version_comment.update_version_comment()
inject_app_metadata.inject(env)

print("[prebuild] ✅ Pre-build sequence completed.")
