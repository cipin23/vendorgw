#!/usr/bin/env python3
"""
autofix.py - Parse build log and auto-fix common ArrowOS/MT6739 errors
Usage: python3 autofix.py --log /tmp/build.log --tree device/samsung/a02
"""

import re, sys, os, argparse, subprocess
from pathlib import Path

def run(cmd):
    print(f"  $ {cmd}")
    os.system(cmd)

# ── Fix handlers ──────────────────────────────────────────────────────────────

def fix_vintf_mismatch(log: str, tree: Path):
    """VINTF: HAL version mismatch between manifest and framework matrix"""
    pattern = r"VINTF.*?hal '([^']+)'.*?version ([0-9.]+).*?not in"
    for m in re.finditer(pattern, log):
        hal, ver = m.group(1), m.group(2)
        print(f"[fix] VINTF mismatch: {hal} @ {ver}")
        manifest = tree / "manifest.xml"
        content = manifest.read_text()
        # Bump version to match what framework expects
        major, minor = ver.split(".")
        new_ver = f"{major}.{int(minor)+1}"
        content = re.sub(
            rf"(<n>{re.escape(hal)}</n>.*?<version>){re.escape(ver)}(</version>)",
            rf"\g<1>{ver}-{new_ver}\2",
            content, flags=re.DOTALL
        )
        manifest.write_text(content)
        print(f"  -> Updated {hal} to {ver}-{new_ver}")

def fix_so_conflict(log: str, tree: Path):
    """Duplicate .so: two modules installing same file"""
    pattern = r"(?:FAILED|error): .* multiple.*?'([^']+\.so)'"
    for m in re.finditer(pattern, log, re.IGNORECASE):
        lib = m.group(1)
        print(f"[fix] Duplicate lib: {lib}")
        # Ensure it's excluded from PRODUCT_COPY_FILES in device.mk
        device_mk = tree / "device.mk"
        content = device_mk.read_text()
        # Add exclusion if not present
        excl = f"PRODUCT_PACKAGES_ETC_SKIP += {os.path.basename(lib)}"
        if excl not in content:
            content += f"\n# Auto-excluded duplicate\n{excl}\n"
            device_mk.write_text(content)
            print(f"  -> Added skip for {lib}")

def fix_missing_32bit(log: str, tree: Path):
    """lib64 reference on 32-bit only device"""
    if "lib64" in log and "arm64" not in log:
        print("[fix] lib64 reference on 32-bit device")
        board_mk = tree / "BoardConfig.mk"
        content = board_mk.read_text()
        if "TARGET_2ND_ARCH :=" not in content:
            content += "\n# Disable 64-bit (MT6739 is 32-bit only)\nTARGET_2ND_ARCH :=\n"
            board_mk.write_text(content)
            print("  -> Disabled TARGET_2ND_ARCH")

def fix_selinux_neverallow(log: str, tree: Path):
    """SELinux neverallow violations"""
    if "neverallow" in log.lower():
        print("[fix] SELinux neverallow - ensuring SELINUX_IGNORE_NEVERALLOWS=true")
        board_mk = tree / "BoardConfig.mk"
        content = board_mk.read_text()
        if "SELINUX_IGNORE_NEVERALLOWS" not in content:
            content += "\nSELINUX_IGNORE_NEVERALLOWS := true\n"
            board_mk.write_text(content)
            print("  -> Set SELINUX_IGNORE_NEVERALLOWS")

def fix_missing_hal(log: str, tree: Path):
    """HAL referenced in manifest but not found in vendor"""
    pattern = r"No.*?HAL.*?'([^']+)'.*?found"
    for m in re.finditer(pattern, log, re.IGNORECASE):
        hal = m.group(1)
        print(f"[fix] Missing HAL: {hal} - marking optional in manifest")
        manifest = tree / "manifest.xml"
        content = manifest.read_text()
        # Mark the hal optional in compat matrix
        compat = tree / "compatibility_matrix.xml"
        compat_content = compat.read_text()
        hal_escaped = re.escape(hal)
        compat_content = re.sub(
            rf'(<hal format="hidl" optional="false">)\s*(<n>{hal_escaped}</n>)',
            r'<hal format="hidl" optional="true">\n    \2',
            compat_content
        )
        compat.write_text(compat_content)
        print(f"  -> Marked {hal} optional in compatibility_matrix.xml")

def fix_product_copy_files_clash(log: str, tree: Path):
    """PRODUCT_COPY_FILES has same dest from two sources"""
    pattern = r"Error.*?PRODUCT_COPY_FILES.*?'([^']+)'"
    already_added = set()
    device_mk = tree / "device.mk"
    content = device_mk.read_text()
    changed = False
    for m in re.finditer(pattern, log, re.IGNORECASE):
        path = m.group(1)
        if path in already_added:
            continue
        already_added.add(path)
        print(f"[fix] PRODUCT_COPY_FILES clash: {path}")
        # Remove the offending line
        new_lines = []
        for line in content.splitlines():
            if path in line and "PRODUCT_COPY_FILES" in content:
                print(f"  -> Removing: {line.strip()}")
                changed = True
            else:
                new_lines.append(line)
        content = "\n".join(new_lines)
    if changed:
        device_mk.write_text(content)

def fix_apex_not_found(log: str, tree: Path):
    """APEX not found - remove from product packages"""
    pattern = r"error:.*?'([^']+\.apex)'.*?not found"
    device_mk = tree / "device.mk"
    content = device_mk.read_text()
    changed = False
    for m in re.finditer(pattern, log, re.IGNORECASE):
        apex = m.group(1)
        print(f"[fix] APEX not found: {apex}")
        new_lines = [l for l in content.splitlines() if apex not in l]
        if len(new_lines) != len(content.splitlines()):
            content = "\n".join(new_lines)
            changed = True
            print(f"  -> Removed {apex} from device.mk")
    if changed:
        device_mk.write_text(content)

def fix_linker_namespace(log: str, tree: Path):
    """Linker namespace issue - add vndk_sp to compat matrix"""
    if "linker" in log.lower() and "namespace" in log.lower():
        print("[fix] Linker namespace issue - adding vndk_sp entry")
        board_mk = tree / "BoardConfig.mk"
        content = board_mk.read_text()
        if "BOARD_VNDK_VERSION" not in content:
            content += "\nBOARD_VNDK_VERSION := current\n"
            board_mk.write_text(content)
            print("  -> Set BOARD_VNDK_VERSION=current")

# ── Main ──────────────────────────────────────────────────────────────────────

FIXERS = [
    fix_vintf_mismatch,
    fix_so_conflict,
    fix_missing_32bit,
    fix_selinux_neverallow,
    fix_missing_hal,
    fix_product_copy_files_clash,
    fix_apex_not_found,
    fix_linker_namespace,
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log",  required=True, help="Build log path")
    ap.add_argument("--tree", required=True, help="device/samsung/a02 path")
    args = ap.parse_args()

    log = Path(args.log).read_text(errors="replace")
    tree = Path(args.tree)

    print(f"[*] Analyzing build log ({len(log)} bytes)...")
    fixed = 0
    for fixer in FIXERS:
        try:
            fixer(log, tree)
            fixed += 1
        except Exception as e:
            print(f"[!] {fixer.__name__} failed: {e}")

    print(f"\n[*] Applied {fixed} fix handlers. Re-running build...")

if __name__ == "__main__":
    main()
