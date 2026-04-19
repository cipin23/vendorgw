$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Inherit vendor blobs configuration (FIX: Pindah dari Android.mk ke sini)
$(call inherit-product, vendor/samsung/a02/a02-vendor.mk)

PRODUCT_NAME := arrow_a02
PRODUCT_DEVICE := a02
PRODUCT_BRAND := samsung
PRODUCT_MODEL := SM-A022F
PRODUCT_MANUFACTURER := samsung

# Inherit ArrowOS common
$(call inherit-product, vendor/arrow/config/common_full_phone.mk)

PRODUCT_GMS_CLIENTID_BASE := android-samsung
