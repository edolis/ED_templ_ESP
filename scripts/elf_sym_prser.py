# generate symbols withxtensa-esp32-elf-nm -S --size-sort -td .pio/build/super_mini_esp32c3_debug/firmware.elf > symbols.txt



import csv
import re

# Input and output file paths
input_file = "symbols.txt"
output_file = "symbols.csv"

# Regex pattern to match symbol lines (adjust if needed)
symbol_pattern = re.compile(r"^([0-9A-Fa-fx]+)\s+(\d+)\s+([a-zA-Z])\s+(.+)$")

# Helper to infer section and bind from type (basic guesswork)
def infer_section_and_bind(symbol_type):
    section = {
        'B': '.bss',
        'D': '.data',
        'T': '.text',
        'R': '.rodata',
        'b': '.bss',
        'd': '.data',
        't': '.text',
        'r': '.rodata'
    }.get(symbol_type, 'unknown')

    bind = 'STB_GLOBAL' if symbol_type.isupper() else 'STB_LOCAL'
    return section, bind

# Parse and write to CSV
with open(input_file, 'r', encoding="utf-16") as infile, open(output_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Name', 'Type', 'Bind', 'Address', 'Section', 'Size'])

    for line in infile:
        match = symbol_pattern.match(line.strip())
        if match:
            address, size, symbol_type, name = match.groups()
            section, bind = infer_section_and_bind(symbol_type)
            writer.writerow([name, f'STT_OBJECT', bind, address, section, size])

print(f"✅ CSV generated: {output_file}")
