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
        parts = git_desc.split("-")

        version_tag = parts[0] if len(parts) > 0 else "v0.0.0"
        tagged_as = parts[1] if len(parts) > 1 else "untagged"
        commit_count = parts[2] if len(parts) > 2 else "0"
        short_hash = parts[3] if len(parts) > 3 else "g0000000"
        dirty_flag = "dirty" if "dirty" in git_desc else ""

        version_string = f"{version_tag}-{commit_count}-{dirty_flag}".strip("-")
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        build_id = f"P{timestamp}-{short_hash[1:]}"  # remove 'g' prefix

        return {
            "version_string": version_string,
            "tagged_as": tagged_as,
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
