#!/usr/bin/env python3
"""
Optimize images for web performance.
- Compress JPG/PNG images
- Convert to WebP format for better compression
- Maintain reasonable quality
"""

import os
from pathlib import Path
from PIL import Image
import sys

# Configuration
QUALITY = 85  # JPG/WebP quality (0-100)
PNG_OPTIMIZE = True  # Optimize PNG files
CONVERT_TO_WEBP = True  # Also create WebP versions
MAX_DIMENSION = 800  # Max width/height for product images

def optimize_image(image_path: Path, create_webp: bool = True) -> dict:
    """
    Optimize a single image file.

    Args:
        image_path: Path to the image file
        create_webp: Whether to create a WebP version

    Returns:
        Dictionary with optimization results
    """
    results = {
        'original_size': 0,
        'new_size': 0,
        'webp_size': 0,
        'savings': 0,
        'error': None
    }

    try:
        # Get original file size
        results['original_size'] = image_path.stat().st_size

        # Open image
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary (for JPG)
            if img.mode == 'RGBA' and image_path.suffix.lower() in ['.jpg', '.jpeg']:
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background

            # Resize if image is too large
            if max(img.size) > MAX_DIMENSION:
                img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)

            # Save optimized version
            if image_path.suffix.lower() in ['.jpg', '.jpeg']:
                img.save(image_path, 'JPEG', quality=QUALITY, optimize=True)
            elif image_path.suffix.lower() == '.png':
                img.save(image_path, 'PNG', optimize=PNG_OPTIMIZE)

            # Get new file size
            results['new_size'] = image_path.stat().st_size
            results['savings'] = results['original_size'] - results['new_size']

            # Create WebP version
            if create_webp and CONVERT_TO_WEBP:
                webp_path = image_path.with_suffix('.webp')
                img.save(webp_path, 'WEBP', quality=QUALITY, method=6)
                results['webp_size'] = webp_path.stat().st_size

    except Exception as e:
        results['error'] = str(e)

    return results


def optimize_directory(directory: Path, max_files: int = None):
    """
    Optimize all images in a directory.

    Args:
        directory: Directory containing images
        max_files: Maximum number of files to process (None = all)
    """
    # Find all images
    image_extensions = {'.jpg', '.jpeg', '.png'}
    images = [
        p for p in directory.rglob('*')
        if p.suffix.lower() in image_extensions
    ]

    if max_files:
        images = images[:max_files]

    total_images = len(images)
    total_original = 0
    total_new = 0
    total_webp = 0
    errors = 0

    print(f"Found {total_images} images to optimize")
    print(f"{'='*60}\n")

    for i, image_path in enumerate(images, 1):
        print(f"[{i}/{total_images}] {image_path.name}...", end=' ')

        results = optimize_image(image_path)

        if results['error']:
            print(f"❌ Error: {results['error']}")
            errors += 1
            continue

        total_original += results['original_size']
        total_new += results['new_size']
        total_webp += results['webp_size']

        savings_pct = (results['savings'] / results['original_size'] * 100) if results['original_size'] > 0 else 0
        print(f"✅ {results['original_size']//1024}KB → {results['new_size']//1024}KB ({savings_pct:.1f}% saved)", end='')

        if results['webp_size'] > 0:
            webp_savings = (results['original_size'] - results['webp_size']) / results['original_size'] * 100
            print(f", WebP: {results['webp_size']//1024}KB ({webp_savings:.1f}% saved)")
        else:
            print()

    # Print summary
    print(f"\n{'='*60}")
    print(f"Optimization Complete!")
    print(f"{'='*60}")
    print(f"Total images processed: {total_images - errors}")
    print(f"Errors: {errors}")
    print(f"Original total size: {total_original / 1024 / 1024:.2f} MB")
    print(f"Optimized total size: {total_new / 1024 / 1024:.2f} MB")
    print(f"WebP total size: {total_webp / 1024 / 1024:.2f} MB")
    print(f"Total savings: {(total_original - total_new) / 1024 / 1024:.2f} MB ({(total_original - total_new) / total_original * 100:.1f}%)")

    if total_webp > 0:
        print(f"WebP savings: {(total_original - total_webp) / 1024 / 1024:.2f} MB ({(total_original - total_webp) / total_original * 100:.1f}%)")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description='Optimize images for web')
    parser.add_argument('directory', nargs='?', default='squish_images', help='Directory containing images')
    parser.add_argument('--max-files', type=int, help='Maximum number of files to process')
    parser.add_argument('--no-webp', action='store_true', help='Skip WebP conversion')

    args = parser.parse_args()

    global CONVERT_TO_WEBP
    if args.no_webp:
        CONVERT_TO_WEBP = False

    directory = Path(args.directory)

    if not directory.exists():
        print(f"Error: Directory {directory} does not exist")
        sys.exit(1)

    optimize_directory(directory, args.max_files)


if __name__ == '__main__':
    main()
