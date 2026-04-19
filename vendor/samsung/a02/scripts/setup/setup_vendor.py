#!/usr/bin/env python3
import argparse, shutil, os
from pathlib import Path

CONFLICT_LIBS = {"libalsautils.so", "libril.so", "libvpx.so", "libdrm.so", "libz.so", "libjpeg.so", "libpng.so"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    args = ap.parse_args()
    
    src = Path(args.src).resolve()
    dst = Path(args.dst).resolve()
    dst.mkdir(parents=True, exist_ok=True)

    # 1. Copy Blobs - Pake penanganan folder yang bener
    for root, dirs, files in os.walk(src):
        for file in files:
            if file == "zImage" or ".git" in root: continue
            s_file = Path(root) / file
            if not s_file.is_file(): continue # Skip kalo bukan file
            
            rel = s_file.relative_to(src)
            d_file = dst / rel
            d_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(s_file, d_file)
            except Exception as e:
                print(f"Skip error file: {e}")

    # 2. Scan hasil copy buat config
    all_f = []
    for root, dirs, files in os.walk(dst):
        for file in files:
            if file in ["Android.bp", "Android.mk", "a02-vendor.mk"]: continue
            p = Path(root) / file
            all_f.append(p.relative_to(dst))

    so_libs = [f for f in all_f if f.suffix == ".so" and f.name not in CONFLICT_LIBS]
    etc_files = [f for f in all_f if f.suffix != ".so"]

    # 3. Write Configs
    bp = ["// Auto-generated BP\n"]
    for lib in so_libs:
        bp += ["cc_prebuilt_library_shared {", f'    name: "vendor_a02_{lib.stem}",', f'    srcs: ["{str(lib)}"],', "    vendor: true, strip: { none: true }, check_elf_files: false, prefer: true,", "}\n"]
    (dst / "Android.bp").write_text("\n".join(bp))

    mk = ["# Auto-generated MK\nPRODUCT_COPY_FILES += \\"]
    entries = [f"    vendor/samsung/a02/{str(f)}:$(TARGET_COPY_OUT_VENDOR)/{str(f)}" for f in etc_files]
    mk.append(" \\\n".join(entries) if entries else "    # empty")
    (dst / "a02-vendor.mk").write_text("\n".join(mk))

    (dst / "Android.mk").write_text("LOCAL_PATH := $(call my-dir)\n\ninclude $(CLEAR_VARS)\n")
    print(f"BINGGO! BP: {len(so_libs)}, MK: {len(etc_files)}")

if __name__ == "__main__":
    main()
