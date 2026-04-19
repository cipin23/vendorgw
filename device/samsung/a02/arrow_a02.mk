# Inherit AOSP
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/product_launched_with_p.mk)

# Inherit device
$(call inherit-product, $(LOCAL_PATH)/device.mk)

# Inherit ArrowOS
$(call inherit-product, vendor/arrow/config/common.mk)

PRODUCT_DEVICE := a02
PRODUCT_NAME   := arrow_a02
PRODUCT_BRAND  := samsung
PRODUCT_MODEL  := SM-A022F
PRODUCT_MANUFACTURER := samsung

PRODUCT_GMS_CLIENTID_BASE := android-samsung
TARGET_VENDOR_PRODUCT_NAME := a02

PRODUCT_BUILD_PROP_OVERRIDES += \
    PRIVATE_BUILD_DESC="a02-user 11 RP1A.200720.012 A022FXXU3BVB1 release-keys" \
    BUILD_FINGERPRINT="samsung/a02/a02:11/RP1A.200720.012/A022FXXU3BVB1:user/release-keys"
