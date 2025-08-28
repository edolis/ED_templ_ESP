# process_sizeInfo.py
import re
import subprocess
import os

# Define which sections to Flash vs RAM
FLASH_SECTIONS = (
    r"\.flash\.text",
    r"\.flash\.rodata",
    r"\.flash\.appdesc",
    r"\.iram0\.text",
)
RAM_SECTIONS = (
    r"\.dram0\.data",
    r"\.dram0\.bss",
)


def format_group(name_sizes, total_label):
    """
    Given a list of (name, size) and a total label, print:
      name1    size1
      name2    size2
      ―――――――――
      total_label    subtotal
    """
    rows = []
    for name, size in name_sizes:
        s = f"{size:,}".replace(",", " ")
        rows.append((name, s))

    subtotal = sum(size for _, size in name_sizes)
    subtotal_str = f"{subtotal:,}".replace(",", " ")

    name_w = max(len(n) for n, _ in rows + [(total_label, "")])
    num_w  = max(len(s) for _, s in rows + [("", subtotal_str)])

    for name, s in rows:
        print(name.ljust(name_w), "  ", s.rjust(num_w), sep="")

    print("―" * (name_w + 2 + num_w))
    print(total_label.ljust(name_w), "  ", subtotal_str.rjust(num_w), sep="")
    print()


def make_side_by_side(flash_list, ram_list):
    """
    Return a list of lines, side-by-side, minimizing rows:
      .flash.text   148 258    .dram0.data   5 144
      …
      subtotal     241 922    total      9 832
    """
    # format sizes
    flash_fmt = [(s, f"{v:,}".replace(",", " ")) for s, v in flash_list]
    ram_fmt   = [(s, f"{v:,}".replace(",", " ")) for s, v in ram_list]

    fw_sec = max((len(s) for s, _ in flash_fmt), default=0)
    fw_num = max((len(n) for _, n in flash_fmt), default=0)
    rw_sec = max((len(s) for s, _ in ram_fmt),   default=0)
    rw_num = max((len(n) for _, n in ram_fmt),   default=0)

    flash_lines = [f"{s.ljust(fw_sec)}  {n.rjust(fw_num)}" for s, n in flash_fmt]
    ram_lines   = [f"{s.ljust(rw_sec)}  {n.rjust(rw_num)}" for s, n in ram_fmt]

    # subtotals
    f_total = sum(v for _, v in flash_list)
    r_total = sum(v for _, v in ram_list)
    flash_lines += [
      "―"*(fw_sec+2+fw_num),
      f"{'subtotal'.ljust(fw_sec)}  {f'{f_total:,}'.replace(',',' ').rjust(fw_num)}"
    ]
    ram_lines += [
      "―"*(rw_sec+2+rw_num),
      f"{'total'.ljust(rw_sec)}  {f'{r_total:,}'.replace(',',' ').rjust(rw_num)}"
    ]

    # pad to equal length
    max_rows = max(len(flash_lines), len(ram_lines))
    flash_lines += [" "*(fw_sec+2+fw_num)]*(max_rows - len(flash_lines))
    ram_lines   += [" "*(rw_sec+2+rw_num)]*(max_rows - len(ram_lines))

    spacer = "    "
    return [flash_lines[i] + spacer + ram_lines[i] for i in range(max_rows)]


def show_size_and_pct(env, elf_path):
    """
    Original behavior: run size, print tables, now also inject them.
    """
    size_tool = env.subst("$SIZETOOL")
    cmd = [size_tool, "-A", "-d", "-t", elf_path]

    try:
        raw = subprocess.check_output(cmd).decode("utf-8", "ignore")
    except Exception as e:
        print("❌ Error running size tool:", e)
        return

    # collect flash & ram sizes
    flash, ram = [], []
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) < 2 or not parts[1].isdigit():
            continue
        sec, sz = parts[0], int(parts[1])
        if any(re.fullmatch(p, sec) for p in FLASH_SECTIONS):
            flash.append((sec, sz))
        elif any(re.fullmatch(p, sec) for p in RAM_SECTIONS):
            ram.append((sec, sz))

    # print to console (unchanged)
    print("\n📦 Flash Sections")
    format_group(flash, "subtotal")
    print("📦 RAM Sections")
    format_group(ram, "total")

    # build side-by-side lines
    table_lines = make_side_by_side(flash, ram)

    # now inject into your app_main .cpp
    _inject_into_cpp(env, table_lines)


def _inject_into_cpp(env, table_lines):
    """
    Find the .cpp under src/ with 'app_main' and replace the
    @compilesize block at its top with table_lines.
    """
    proj_dir = env.subst("$PROJECT_DIR")
    src_dir  = os.path.join(proj_dir, "src")
    pattern  = re.compile(
        r"\*\s*@compilesize\s+begin.*?@compilesize\s+end\s*\n\s*\*",
        re.DOTALL
    )

    for root, _, files in os.walk(src_dir):
        for fn in files:
            if fn.endswith(".cpp"):
                path = os.path.join(root, fn)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "app_main" not in content:
                    continue

                # build replacement block
                block = ["*  @compilesize begin\n"]
                for ln in table_lines:
                    block.append("    " + ln)  # 4-space indent
                block.append("\n    @compilesize end")
                block.append(" *")  # final line

                new_block = "\n".join(block)

                # replace and write back
                new_content = pattern.sub(new_block, content)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                print(f"✅ Injected compile-size tables into {path}")
                return

    print("⚠️  Could not find app_main .cpp under src/ to inject.")
