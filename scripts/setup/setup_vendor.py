#!/usr/bin/env python3
import argparse, shutil, os
from pathlib import Path

# Daftar lib yang dilarang (bikin error build)
CONFLICT_LIBS = {"libalsautils.so", "libril.so", "libvpx.so", "libdrm.so", "libz.so", "libjpeg.so", "libpng.so"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    args = ap.parse_args()
    
    dst = Path(args.dst).resolve()
    src = Path(args.src).resolve()
    
    # 1. Pastiin folder tujuan ada dan bersih
    dst.mkdir(parents=True, exist_ok=True)

    # 2. Copy semua file dari vendor_src ke out_repo
    print(f"Copying files from {src} to {dst}...")
    for f in src.rglob("*"):
        if f.is_file() and ".git" not in f.parts and f.name != "zImage":
            rel_path = f.relative_to(src)
            target_file = dst / rel_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target_file)

    # 3. List semua file yang udah di-copy buat bikin config
    all_files = []
    for root, dirs, files in os.walk(dst):
        for file in files:
            # Lewatin file config itu sendiri biar ga looping
            if file in ["Android.bp", "Android.mk", "a02-vendor.mk"]:
                continue
            
            p = Path(os.path.join(root, file))
            all_files.append(p.relative_to(dst))

    so_libs = [f for f in all_files if f.suffix == ".so" and f.name not in CONFLICT_LIBS]
    etc_files = [f for f in all_files if f.suffix != ".so"]

    # 4. Tulis Android.bp (Buat Shared Libraries)
    bp_content = ["// Auto-generated Vendor Blobs BP", ""]
    for lib in so_libs:
        bp_content += [
            "cc_prebuilt_library_shared {",
            f'    name: "vendor_a02_{lib.stem}",',
            f'    srcs: ["{str(lib)}"],',
            "    vendor: true,",
            "    strip: { none: true },",
            "    check_elf_files: false,",
            "    prefer: true,",
            "}", ""
        ]
    (dst / "Android.bp").write_text("\n".join(bp_content))

    # 5. Tulis a02-vendor.mk (Buat PRODUCT_COPY_FILES)
    mk_content = ["# Auto-generated Vendor Blobs MK", "PRODUCT_COPY_FILES += \\"]
    entries = [f"    vendor/samsung/a02/{str(f)}:$(TARGET_COPY_OUT_VENDOR)/{str(f)}" for f in etc_files]
    if entries:
        mk_content.append(" \\\n".join(entries))
    else:
        mk_content.append("    # No etc files found")
    (dst / "a02-vendor.mk").write_text("\n".join(mk_content))

    # 6. Tulis Android.mk (Boilerplate)
    (dst / "Android.mk").write_text("LOCAL_PATH := $(call my-dir)\n\ninclude $(CLEAR_VARS)\n")
    
    print(f"Success! BP: {len(so_libs)} | MK: {len(etc_files)}")

if __name__ == "__main__":
    main()
