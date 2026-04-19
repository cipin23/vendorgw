#!/usr/bin/env python3
import argparse, shutil, os
from pathlib import Path

CONFLICT_LIBS = {"libalsautils.so", "libril.so", "libvpx.so", "libdrm.so", "libz.so", "libjpeg.so", "libpng.so"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    args = ap.parse_args()
    
    # Path absolut biar gak nyasar
    src = Path(args.src).resolve()
    dst = Path(args.dst).resolve()
    
    print(f"[*] Sumber: {src}")
    print(f"[*] Target: {dst}")

    if not src.exists():
        print("[-] ERROR: Folder sumber gak ada!")
        return

    dst.mkdir(parents=True, exist_ok=True)

    # 1. Copy file blobs
    for root, dirs, files in os.walk(src):
        for file in files:
            if file == "zImage" or ".git" in root:
                continue
            s_file = Path(root) / file
            rel = s_file.relative_to(src)
            d_file = dst / rel
            d_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s_file, d_file)

    # 2. Scan hasil copy buat bikin config
    so_libs = []
    etc_files = []
    for root, dirs, files in os.walk(dst):
        for file in files:
            if file in ["Android.bp", "Android.mk", "a02-vendor.mk"]:
                continue
            p = Path(root) / file
            rel = p.relative_to(dst)
            if p.suffix == ".so" and file not in CONFLICT_LIBS:
                so_libs.append(rel)
            elif p.suffix != ".so":
                etc_files.append(rel)

    # 3. Write Android.bp
    bp = ["// Auto-generated\n"]
    for lib in so_libs:
        bp += [
            "cc_prebuilt_library_shared {",
            f'    name: "vendor_a02_{lib.stem}",',
            f'    srcs: ["{str(lib)}"],',
            "    vendor: true, strip: { none: true }, check_elf_files: false, prefer: true,",
            "}\n"
        ]
    (dst / "Android.bp").write_text("\n".join(bp))

    # 4. Write a02-vendor.mk (INI YANG LOE CARI)
    mk = ["PRODUCT_COPY_FILES += \\"]
    entries = [f"    vendor/samsung/a02/{str(f)}:$(TARGET_COPY_OUT_VENDOR)/{str(f)}" for f in etc_files]
    mk.append(" \\\n".join(entries) if entries else "    # empty")
    (dst / "a02-vendor.mk").write_text("\n".join(mk))

    # 5. Write Android.mk
    (dst / "Android.mk").write_text("LOCAL_PATH := $(call my-dir)\n\ninclude $(CLEAR_VARS)\n")
    print(f"[+] Selesai! BP: {len(so_libs)}, MK: {len(etc_files)}")

if __name__ == "__main__":
    main()
