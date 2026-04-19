name: 1. Setup Vendor & Device Tree

on:
  workflow_dispatch:

env:
  VENDOR_REPO: cipin23/vendorgw

jobs:
  setup-trees:
    runs-on: ubuntu-22.04
    steps:
    - name: Checkout target repo
      uses: actions/checkout@v4
      with:
        path: out_repo

    - name: Clone vendor blobs
      run: git clone --depth=1 https://github.com/$VENDOR_REPO.git vendor_src

    - name: Generate Trees
      run: |
        # Bersihin folder lama
        rm -rf out_repo/vendor/samsung/a02
        rm -rf out_repo/device/samsung/a02
        mkdir -p out_repo/vendor/samsung/a02
        mkdir -p out_repo/device/samsung/a02

        # Run Setup (Pastikan --src ke vendor_src)
        python3 out_repo/scripts/setup/setup_vendor.py \
          --src vendor_src \
          --dst out_repo/vendor/samsung/a02
        
        # Run Device Tree Gen
        python3 out_repo/scripts/setup/gen_device_tree.py \
          --vendor-src vendor_src \
          --out out_repo/device/samsung/a02

    - name: Copy zImage
      run: |
        mkdir -p out_repo/device/samsung/a02/prebuilt
        cp vendor_src/zImage out_repo/device/samsung/a02/prebuilt/zImage || echo "No zImage"

    - name: Commit & Push
      run: |
        cd out_repo
        git config user.name "Arrow Tree Bot"
        git config user.email "bot@arrow.local"
        # Force add semua file baru
        git add .
        # Cek status buat debug di log
        git status
        # Commit & Push
        git commit -m "Fix: Re-generate vendor tree with a02-vendor.mk [skip ci]" || exit 0
        git push
