#!/usr/bin/env python3
import argparse, shutil
from pathlib import Path

CONFLICT_LIBS = {"libalsautils.so", "libril.so", "libvpx.so", "libdrm.so", "libz.so", "libjpeg.so", "libpng.so"}

def write_bp(dst: Path, so_libs: list):
    lines = ["// Auto-generated BP", ""]
    for lib in so_libs:
        lines += ["cc_prebuilt_library_shared {", f'    name: "vendor_a02_{lib.stem}",', f'    srcs: ["{lib.name}"],', "    vendor: true, check_elf_files: false, prefer: true,", "}", ""]
    (dst / "Android.bp").write_text("\n".join(lines))

def write_vendor_mk(dst: Path, etc_files: list):
    lines = ["PRODUCT_COPY_FILES += \\"]
    entries = [f"    vendor/samsung/a02/{f}:$(TARGET_COPY_OUT_VENDOR)/{f}" for f in etc_files]
    lines.append(" \\\n".join(entries) if entries else " # empty")
    (dst / "a02-vendor.mk").write_text("\n".join(lines))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    args = ap.parse_args()
    dst = Path(args.dst).resolve()
    src = Path(args.src).resolve()
    
    for f in src.rglob("*"):
        if f.is_file() and ".git" not in f.parts and f.name != "zImage":
            rel = f.relative_to(src)
            (dst / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst / rel)

    all_f = [f.relative_to(dst) for f in dst.rglob("*") if f.is_file()]
    so_libs = [f for f in all_f if f.suffix == ".so" and f.name not in CONFLICT_LIBS]
    etc_files = [str(f) for f in all_f if f.suffix != ".so" and f.name not in ["Android.bp", "Android.mk", "a02-vendor.mk"]]

    write_bp(dst, so_libs)
    write_vendor_mk(dst, etc_files)
    (dst / "Android.mk").write_text("LOCAL_PATH := $(call my-dir)\n\ninclude $(CLEAR_VARS)\n")

if __name__ == "__main__":
    main()
