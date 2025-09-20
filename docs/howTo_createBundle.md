# X 509 bundle
Basically you are merging your certification Authority ceritficate to the autorities predefined as trusted by ESP, so that the certificate is trusted by the ESP32 and used to validate the connection to MQTT.

The alternative approach is embed the certificate and load it in the RAM< but this causes fragmentation of the memory and periodic crash as soon as the fragmentation does not allow to allocate the large memory block for the certificate.> - this when using TSL for Mosquitto, which, in case of instability and hight traffic, often needs reconnects.
## generation

In this setup, the bundle is generated manually, reason being that Platformio does NOT invoke the bundler, as the CMakeLists command which should invoke gen_crt_bundle.py when CONFIG_MBEDTLS_CERTIFICATE_BUNDLE is set is emptied out
```
if(CONFIG_MBEDTLS_CERTIFICATE_BUNDLE)
    list(APPEND include_dirs "${COMPONENT_DIR}/esp_crt_bundle/include")
endif()
```
---

# 📜 ESP‑IDF / PlatformIO — Merging Custom CA with Mozilla Roots for Static X.509 Bundle

## 1️⃣ Merge Your CA with the Standard Mozilla Roots

From the ESP‑IDF `esp_crt_bundle` directory:

```cmd
cd D:\Espressif\esp-idf-v5.5\components\mbedtls\esp_crt_bundle

:: Merge cacrt_all.pem (Mozilla roots) + your ca.pem into one PEM
type "cacrt_all.pem" "%ESP_HEADERS%\ca.pem" > "%ESP_HEADERS%\merged_roots.pem"
```

> 💡 `type` works in CMD even with quoted paths.
> `%ESP_HEADERS%` is your environment variable pointing to `D:\MyStuff\Software\VSrepos\sharedIncludes`.

---

## 2️⃣ Generate the Binary Certificate Bundle

Run the generator on the merged PEM:

```cmd
python gen_crt_bundle.py --input "%ESP_HEADERS%\merged_roots.pem"
```

This produces a **binary** file named:

```
x509_crt_bundle   (no extension)
```

in the current directory.

---

## 3️⃣ Create the Assembly Wrapper (`.S`)

Move the binary to your shared folder:

```cmd
copy /y "x509_crt_bundle" "%ESP_HEADERS%\x509_crt_bundle"
```

Create `%ESP_HEADERS%\x509_crt_bundle.S` with the following content:

```asm
    .section .rodata
    .global _binary_x509_crt_bundle_start
    .global _binary_x509_crt_bundle_end
    .align 4

_binary_x509_crt_bundle_start:
    .incbin "x509_crt_bundle"
_binary_x509_crt_bundle_end:
```

> 📌 This `.S` file references the binary via `.incbin` and defines the exact linker symbols the ESP‑IDF crt‑bundle code expects.

---

## 4️⃣ Include the `.S` in Your Build

In your component’s `CMakeLists.txt` (PlatformIO: `src/CMakeLists.txt` or equivalent):

```cmake
set(ESP_HEADERS_DIR $ENV{ESP_HEADERS})

idf_component_register(
    SRCS
        ${app_sources}
        "${ESP_HEADERS_DIR}/x509_crt_bundle.S"
    INCLUDE_DIRS
        "."
        "${ESP_HEADERS_DIR}"
)
```

---

## 5️⃣ Configure `sdkconfig` / `sdkconfig.defaults`

Enable the bundle subsystem and tell it to use your custom bundle:

```ini
CONFIG_MBEDTLS_CERTIFICATE_BUNDLE=y
CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE=y
# CONFIG_MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL is not set
```

> ❗ Make sure `CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH` is **unset** (empty) — otherwise CMake will try to regenerate the bundle from that path.

---

## 6️⃣ Verify at Build Time

After a clean build (`pio run -t clean`), check that the linker symbols are present:

```cmd
riscv32-esp-elf-nm -g .pio\build\<env>\firmware.elf | findstr /I x509_crt_bundle
```

Expected output:

```
... D _binary_x509_crt_bundle_start
... D _binary_x509_crt_bundle_end
```

---

## 7️⃣ Runtime Check

If the CA is correct and matches the broker’s chain, TLS should succeed without:

```
esp-x509-crt-bundle: No matching trusted root certificate found
```

If you still see that, dump the broker’s chain with:

```bash
openssl s_client -connect broker.example.com:8883 -showcerts
```

…and confirm the root CA is in your merged PEM.

---

✅ **Summary Flow:**
1. Merge `cacrt_all.pem` + `ca.pem` → `merged_roots.pem`
2. Run `gen_crt_bundle.py` → `x509_crt_bundle` (binary)
3. Create `.S` wrapper with `.incbin`
4. Add `.S` to CMake `SRCS`
5. Set `sdkconfig` flags for custom bundle
6. Verify linker symbols in ELF
7. Test TLS connection

---

If you want, I can also prepare a **single Windows batch script** that does steps 1–3 automatically so you can regenerate the bundle in one command whenever your CA changes. That would make this process completely repeatable. Would you like me to make that?