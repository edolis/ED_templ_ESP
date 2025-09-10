## to get back the cocation of the code crashing

- form the crash get the MEPC (like ```MEPC    : 0x42000cb2 ```)
- use in a bash
```
 /D/Espressif/tools/riscv32-esp-elf/esp-13.2.0_20240530/riscv32-esp-elf/bin/riscv32-esp-elf-addr2line.exe -pfiaC -e .pio/build/main_noBT/firmware.elf 0x42000cb2
 ```

## to build symbols.txt to analyze memory usage

```/D/Espressif/tools/tools/riscv32-esp-elf/esp-14.2.0_20241119/riscv32-esp-elf/bin/riscv32-esp-elf-nm.exe -S --size-sort .pio/build/main_noBT/firmware.elf>symbols.txt
```

launch **elf_sym_prser.py**