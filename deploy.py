#!/usr/bin/env python3
"""Deploy squishmallowdex to /docs for GitHub Pages."""

import os
import shutil
from pathlib import Path


def deploy():
    """Deploy the collection to /docs directory for GitHub Pages."""
    root = Path(__file__).parent
    docs = root / "docs"

    print("🚀 Starting deployment to /docs...")

    # Create directory structure
    print("📁 Creating directory structure...")
    (docs / "assets" / "css").mkdir(parents=True, exist_ok=True)
    (docs / "assets" / "images").mkdir(parents=True, exist_ok=True)

    # Copy main collection file
    print("📄 Copying squishmallowdex.html...")
    src_html = root / "squishmallowdex.html"
    if src_html.exists():
        shutil.copy(src_html, docs / "squishmallowdex.html")
        size_mb = src_html.stat().st_size / (1024 * 1024)
        print(f"   ✅ Copied ({size_mb:.1f} MB)")
    else:
        print("   ⚠️  squishmallowdex.html not found - run squishmallowdex.py first!")

    # Copy images directory
    print("🖼️  Copying squish_images...")
    src_images = root / "squish_images"
    dest_images = docs / "squish_images"

    if src_images.exists():
        if dest_images.exists():
            shutil.rmtree(dest_images)
        shutil.copytree(src_images, dest_images)
        image_count = len(list(dest_images.glob("*")))
        print(f"   ✅ Copied {image_count} images")
    else:
        print("   ⚠️  squish_images/ not found - run squishmallowdex.py first!")

    # Copy logo assets
    print("🎨 Copying logo assets...")
    logo_files = ["squishmallowdex.png", "icon-192.png", "icon-512.png"]
    copied_logos = 0

    for img in logo_files:
        src = root / img
        if src.exists():
            shutil.copy(src, docs / "assets" / "images" / img)
            copied_logos += 1

    if copied_logos > 0:
        print(f"   ✅ Copied {copied_logos} logo files")
    else:
        print("   ⚠️  No logo files found")

    # Verify deployment
    print("\n🔍 Verifying deployment...")
    required_files = [
        "index.html",
        "about.html",
        "guide.html",
        "404.html",
        "squishmallowdex.html",
        "assets/css/shared.css",
        ".nojekyll",
    ]

    all_present = True
    for file in required_files:
        if (docs / file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} missing")
            all_present = False

    # Summary
    print("\n" + "="*50)
    if all_present:
        print("✅ Deployment successful!")
        print(f"📂 All files deployed to: {docs}")
        print("\nNext steps:")
        print("1. Commit changes: git add docs/")
        print("2. Push to GitHub: git push")
        print("3. Enable GitHub Pages in repository settings")
        print("   - Source: Deploy from a branch")
        print("   - Branch: main")
        print("   - Folder: /docs")
    else:
        print("⚠️  Deployment completed with warnings")
        print("Some files are missing. Please check the output above.")
    print("="*50)


if __name__ == "__main__":
    deploy()
