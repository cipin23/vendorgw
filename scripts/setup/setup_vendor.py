#!/usr/bin/env python3
import argparse, shutil, os
from pathlib import Path

# Daftar lib yang sering bikin build error
CONFLICT_LIBS = {"libalsautils.so", "libril.so", "libvpx.so", "libdrm.so", "libz.so", "libjpeg.so", "libpng.so"}

def write_bp(dst: Path, so_libs: list):
    lines = ["// Auto-generated BP", ""]
    for lib in so_libs:
        lines += ["cc_prebuilt_library_shared {", f'    name: "vendor_a02_{lib.stem}",', f'    srcs: ["{lib.name}"],', "    vendor: true, check_elf_files: false, prefer: true,", "}", ""]
    (dst / "Android.bp").write_text("\n".join(lines))

def write_vendor_mk(dst: Path, etc_files: list):
    lines = ["PRODUCT_COPY_FILES += \\"]
    # Daftarin semua file non-so ke PRODUCT_COPY_FILES
    entries = [f"    vendor/samsung/a02/{f}:$(TARGET_COPY_OUT_VENDOR)/{f}" for f in etc_files]
    if entries:
        lines.append(" \\\n".join(entries))
    else:
        lines.append("    # empty")
    (dst / "a02-vendor.mk").write_text("\n".join(lines))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    args = ap.parse_args()
    dst = Path(args.dst).resolve()
    src = Path(args.src).resolve()
    
    # 1. Copy smua file beneran dari sumber ke folder repo
    if src.exists():
        for f in src.rglob("*"):
            if f.is_file() and ".git" not in f.parts and f.name != "zImage":
                rel = f.relative_to(src)
                target = dst / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, target)

    # 2. Ambil list file yang udah di-copy buat dibikin config
    # Scan ulang folder dst setelah copy selesai
    all_f = [f.relative_to(dst) for f in dst.rglob("*") if f.is_file()]
    
    # Pisahin mana .so mana yang bukan
    so_libs = [f for f in all_f if f.suffix == ".so" and f.name not in CONFLICT_LIBS]
    # Kecualikan file meta (bp/mk) dari daftar copy
    etc_files = [str(f) for f in all_f if f.suffix != ".so" and f.name not in ["Android.bp", "Android.mk", "a02-vendor.mk"]]

    # 3. Tulis file-file sakti
    write_bp(dst, so_libs)
    write_vendor_mk(dst, etc_files)
    (dst / "Android.mk").write_text("LOCAL_PATH := $(call my-dir)\n\ninclude $(CLEAR_VARS)\n")
    print(f"DONE -> BP: {len(so_libs)} | MK: {len(etc_files)}")

if __name__ == "__main__":
    main()
