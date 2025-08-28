import subprocess
import re
import os
from datetime import datetime

def update_version_comment():
    def get_git_description():
        try:
            return subprocess.check_output(
                ["git", "describe", "--tags", "--long", "--dirty"],
                stderr=subprocess.DEVNULL
            ).decode("utf-8").strip()
        except subprocess.CalledProcessError:
            return "v0.0.0-untagged-0-g0000000-dirty"

    def get_full_commit_hash():
        try:
            return subprocess.check_output(
                ["git", "rev-parse", "HEAD"]
            ).decode("utf-8").strip()
        except subprocess.CalledProcessError:
            return "0000000000000000000000000000000000000000"

    def build_version_data(git_desc, full_hash):
        # Example: v1.0.0.0-SNTP-core-0-g5d100c9-dirty
        match = re.match(r"^(v[\d\.]+)-(.*)-(\d+)-(g[0-9a-f]+)(-dirty)?$", git_desc)
        if not match:
            return {
                "version_string": "v0.0.0-0",
                "tagged_as": "untagged",
                "short_hash": "g0000000",
                "full_hash": full_hash,
                "build_id": "P00000000-000000-0000000"
            }

        version_prefix = match.group(1)     # v1.0.0.0
        tag_name = match.group(2)           # SNTP-core
        commit_count = match.group(3)       # 0
        short_hash = match.group(4)         # g5d100c9
        dirty_flag = match.group(5)         # -dirty or None

        version_string = f"{version_prefix}-{commit_count}"
        if dirty_flag:
            version_string += "-dirty"

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        build_id = f"P{timestamp}-{short_hash[1:]}"  # remove 'g'

        return {
            "version_string": version_string,
            "tagged_as": tag_name,
            "short_hash": short_hash,
            "full_hash": full_hash,
            "build_id": build_id
        }

    def find_app_main_file():
        for root, _, files in os.walk("src"):
            for file in files:
                if file.endswith(".cpp"):
                    full_path = os.path.join(root, file)
                    with open(full_path, "r", encoding="utf-8") as f:
                        if "app_main" in f.read():
                            return full_path
        return None

    target_file = find_app_main_file()
    if not target_file:
        print("❌ Could not find a .cpp file containing 'app_main' in src/")
        return

    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()

    git_desc = get_git_description()
    full_hash = get_full_commit_hash()
    data = build_version_data(git_desc, full_hash)

    # Update comment block
    version_block = (
        f"/**\n"
        f" * @version GIT_VERSION: {data['version_string']}\n"
        f" * @tagged as : {data['tagged_as']}\n"
        f" * @commit hash: {data['short_hash']} [{data['full_hash']}]\n"
        f" * @build ID: {data['build_id']}\n"
        f" */"
    )

    content = re.sub(
        r"/\*\*.*?@version GIT_VERSION:.*?\*/",
        version_block,
        content,
        flags=re.DOTALL
    )

    # Update fwInfo struct fields
    replacements = {
        "GIT_VERSION": data["version_string"],
        "GIT_TAG": data["tagged_as"],
        "GIT_HASH": data["short_hash"],
        "FULL_HASH": data["full_hash"],
        "BUILD_ID": data["build_id"]
    }

    for key, value in replacements.items():
        pattern = rf'(static constexpr const char\* {key}\s*=\s*")[^"]*(")'
        replacement = rf'\g<1>{value}\g<2>'
        content = re.sub(pattern, replacement, content)

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Version info updated in: {target_file}")

# Entry point
if __name__ == "__main__":
    update_version_comment()
