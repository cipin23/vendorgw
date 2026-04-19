#!/usr/bin/env python3
"""
gen_device_tree.py - FIXED: Tambah inherit vendor mk untuk fix readonly PRODUCT_COPY_FILES
"""

import os, argparse
from pathlib import Path

# ── Device constants ──────────────────────────────────────────────────────────
DEVICE_VARS = {
    "DEVICE_PATH":            "device/samsung/a02",
    "BOARD_VENDOR":           "samsung",
    "TARGET_DEVICE":          "a02",
    "TARGET_PRODUCT":         "arrow_a02",
    "PRODUCT_MANUFACTURER":   "samsung",
    "PRODUCT_BRAND":          "samsung",
    "PRODUCT_MODEL":          "SM-A022F",
    "PRODUCT_NAME":           "arrow_a02",
    "TARGET_BOARD_PLATFORM":  "mt6739",
    "TARGET_BOOTLOADER_BOARD_NAME": "k39tv1_bsp_titan_hamster",
    "TARGET_NO_BOOTLOADER":   "true",
    # ARM 32-bit (Sesuai koreksi user)
    "TARGET_ARCH":            "arm",
    "TARGET_ARCH_VARIANT":    "armv8-a",
    "TARGET_CPU_ABI":         "armeabi-v7a",
    "TARGET_CPU_ABI2":        "armeabi",
    "TARGET_CPU_VARIANT":     "cortex-a53",
    # Kernel
    "BOARD_KERNEL_BASE":      "0x40000000",
    "BOARD_KERNEL_PAGESIZE":  "2048",
    "BOARD_KERNEL_OFFSET":    "0x00008000",
    "BOARD_RAMDISK_OFFSET":   "0x01100000",
    "BOARD_TAGS_OFFSET":      "0x00000100",
    "BOARD_KERNEL_CMDLINE":   "bootopt=64S3,32N2,64N2 buildvariant=userdebug",
}

# ── Templates ─────────────────────────────────────────────────────────────────

BOARD_CONFIG_MK = """
DEVICE_PATH := {DEVICE_PATH}

# Architecture
TARGET_ARCH := {TARGET_ARCH}
TARGET_ARCH_VARIANT := {TARGET_ARCH_VARIANT}
TARGET_CPU_ABI := {TARGET_CPU_ABI}
TARGET_CPU_ABI2 := {TARGET_CPU_ABI2}
TARGET_CPU_VARIANT := {TARGET_CPU_VARIANT}
TARGET_CPU_SMP := true
TARGET_USES_64_BIT_BINDER := true

# Kernel
BOARD_KERNEL_BASE := {BOARD_KERNEL_BASE}
BOARD_KERNEL_PAGESIZE := {BOARD_KERNEL_PAGESIZE}
BOARD_KERNEL_OFFSET := {BOARD_KERNEL_OFFSET}
BOARD_RAMDISK_OFFSET := {BOARD_RAMDISK_OFFSET}
BOARD_TAGS_OFFSET := {BOARD_TAGS_OFFSET}
BOARD_KERNEL_CMDLINE := {BOARD_KERNEL_CMDLINE}
TARGET_PREBUILT_KERNEL := $(DEVICE_PATH)/prebuilt/zImage

# Partitions
BOARD_FLASH_BLOCK_SIZE := 131072
BOARD_BOOTIMAGE_PARTITION_SIZE := 33554432
BOARD_RECOVERYIMAGE_PARTITION_SIZE := 33554432
BOARD_SYSTEMIMAGE_PARTITION_SIZE := 3221225472
BOARD_USERDATAIMAGE_PARTITION_SIZE := 25769803776

# Dynamic Partitions
BOARD_SUPER_PARTITION_SIZE := 9126805504
BOARD_SUPER_PARTITION_GROUPS := samsung_dynamic_partitions
BOARD_SAMSUNG_DYNAMIC_PARTITIONS_SIZE := 9122611200
BOARD_SAMSUNG_DYNAMIC_PARTITIONS_PARTITION_LIST := system vendor product

# Platform
TARGET_BOARD_PLATFORM := {TARGET_BOARD_PLATFORM}
TARGET_BOOTLOADER_BOARD_NAME := {TARGET_BOOTLOADER_BOARD_NAME}
TARGET_NO_BOOTLOADER := {TARGET_NO_BOOTLOADER}

# VINTF
DEVICE_MANIFEST_FILE := $(DEVICE_PATH)/manifest.xml
DEVICE_MATRIX_FILE := $(DEVICE_PATH)/compatibility_matrix.xml
""".format(**DEVICE_VARS)

ARROW_MK = """
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Inherit vendor blobs configuration (FIX: Pindah dari Android.mk ke sini)
$(call inherit-product, vendor/samsung/a02/a02-vendor.mk)

PRODUCT_NAME := {PRODUCT_NAME}
PRODUCT_DEVICE := {TARGET_DEVICE}
PRODUCT_BRAND := {PRODUCT_BRAND}
PRODUCT_MODEL := {PRODUCT_MODEL}
PRODUCT_MANUFACTURER := {PRODUCT_MANUFACTURER}

# Inherit ArrowOS common
$(call inherit-product, vendor/arrow/config/common_full_phone.mk)

PRODUCT_GMS_CLIENTID_BASE := android-samsung
""".format(**DEVICE_VARS)

ANDROID_PRODUCTS_MK = """
PRODUCT_MAKEFILES := \\
    $(LOCAL_DIR)/arrow_{TARGET_DEVICE}.mk
""".format(**DEVICE_VARS)

MANIFEST_XML = """
<manifest version="1.0" type="device">
    <hal format="hidl">
        <name>android.hardware.health</name>
        <transport>hwbinder</transport>
        <version>2.1</version>
        <interface>
            <name>IHealth</name>
            <instance>default</instance>
        </interface>
    </hal>
</manifest>
"""

COMPAT_MATRIX_XML = """
<compatibility-matrix version="1.0" type="device">
    <hal format="hidl" optional="false">
        <name>android.hardware.health</name>
        <version>2.1</version>
        <interface>
            <name>IHealth</name>
            <instance>default</instance>
        </interface>
    </hal>
</compatibility-matrix>
"""

# ── Generator Logic ──────────────────────────────────────────────────────────

def write(path: Path, content: str):
    path.write_text(content.strip() + "\n")
    print(f"[+] Generated: {path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vendor-src", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    write(out / "BoardConfig.mk",     BOARD_CONFIG_MK)
    write(out / "AndroidProducts.mk", ANDROID_PRODUCTS_MK)
    write(out / f"arrow_{DEVICE_VARS['TARGET_DEVICE']}.mk", ARROW_MK)
    write(out / "manifest.xml",       MANIFEST_XML)
    write(out / "compatibility_matrix.xml", COMPAT_MATRIX_XML)

    # Prebuilt & sepolicy
    (out / "prebuilt").mkdir(exist_ok=True)
    (out / "sepolicy/vendor").mkdir(parents=True, exist_ok=True)
    write(out / "sepolicy/vendor/file_contexts", "# vendor sepolicy for a02\n")

    # Overlay
    val_path = out / "overlay/frameworks/base/core/res/res/values"
    val_path.mkdir(parents=True, exist_ok=True)
    write(val_path / "config.xml", 
          '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
          '    <integer name="config_screenDensityDpi">300</integer>\n'
          '</resources>')

if __name__ == "__main__":
    main()
