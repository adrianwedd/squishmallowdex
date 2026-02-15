#!/usr/bin/env python3
"""
Generate Open Graph image for social media sharing.
Creates a 1200x630px image for optimal display on social platforms.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Image dimensions (Open Graph standard)
WIDTH = 1200
HEIGHT = 630

# Colors (Squishmallows brand colors - pastel pink/purple theme)
BG_COLOR = '#FFE5F3'  # Light pink
TEXT_COLOR = '#4A4A4A'  # Dark gray
ACCENT_COLOR = '#FF69B4'  # Hot pink

def create_og_image(output_path='og-image.png'):
    """
    Create an Open Graph image with Squishmallowdex branding.

    Args:
        output_path: Path where the image will be saved
    """
    # Create image with background color
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to use system fonts, fall back to default if not available
    try:
        # Try to load a nice sans-serif font
        title_font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 90)
        subtitle_font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 40)
    except:
        try:
            # Fallback for macOS
            title_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 90)
            subtitle_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 40)
        except:
            # Use default font if no system fonts available
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()

    # Add decorative border
    border_width = 20
    draw.rectangle(
        [(border_width, border_width), (WIDTH - border_width, HEIGHT - border_width)],
        outline=ACCENT_COLOR,
        width=8
    )

    # Add title text
    title = "Squishmallowdex"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    title_x = (WIDTH - title_width) // 2
    title_y = 180

    # Draw title with shadow effect
    draw.text((title_x + 3, title_y + 3), title, fill='#00000020', font=title_font)
    draw.text((title_x, title_y), title, fill=TEXT_COLOR, font=title_font)

    # Add subtitle
    subtitle = "Complete Squishmallows Database"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (WIDTH - subtitle_width) // 2
    subtitle_y = title_y + title_height + 30

    draw.text((subtitle_x, subtitle_y), subtitle, fill=TEXT_COLOR, font=subtitle_font)

    # Add decorative circles (like squishmallows!)
    circle_colors = ['#FFB6D9', '#D4A5D4', '#A8D8EA', '#FFE5A0']
    circle_radius = 60

    # Bottom left circles
    for i, color in enumerate(circle_colors[:2]):
        x = 100 + (i * 80)
        y = HEIGHT - 120
        draw.ellipse(
            [(x - circle_radius, y - circle_radius),
             (x + circle_radius, y + circle_radius)],
            fill=color,
            outline=ACCENT_COLOR,
            width=3
        )

    # Top right circles
    for i, color in enumerate(circle_colors[2:]):
        x = WIDTH - 200 - (i * 80)
        y = 120
        draw.ellipse(
            [(x - circle_radius, y - circle_radius),
             (x + circle_radius, y + circle_radius)],
            fill=color,
            outline=ACCENT_COLOR,
            width=3
        )

    # Save the image
    img.save(output_path, 'PNG', optimize=True)
    print(f"✅ Open Graph image created: {output_path}")
    print(f"   Dimensions: {WIDTH}x{HEIGHT}px")

    # Get file size
    file_size = os.path.getsize(output_path)
    print(f"   Size: {file_size / 1024:.1f} KB")

if __name__ == '__main__':
    create_og_image()
