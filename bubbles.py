from PIL import Image, ImageDraw, ImageFont, ImageOps
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from moviepy.video.fx.all import crop


font_path = "C:\\Windows\\Fonts\\arial.ttf"  # Windows path example


def paste_with_transparency(target_image, image_to_paste, position):
    """
    Pastes an image onto another image at a specified position, handling transparency.
    """
    if image_to_paste.mode in ('RGBA', 'LA') or (image_to_paste.mode == 'P' and 'transparency' in image_to_paste.info):
        # Use alpha channel as mask
        target_image.paste(image_to_paste, position, image_to_paste)
    else:
        # No transparency to handle
        target_image.paste(image_to_paste, position)

def wrap_text(text, font, max_width):
    lines = []
    words = text.split()
    while words:
        line = ''
        while words and font.getsize(line + words[0])[0] <= max_width:
            line += (words.pop(0) + ' ')
        lines.append(line.strip())
    return lines

padding = 10
reddit_logo_padding = 10
inner_padding = 10
logo_size = 55  # Adjust for the actual size of your logo
button_height = 35  # Adjust based on your button image height
subberLeftPadding = 20


reddit_logo_path = "assets\\reddit_logo.jpg"
subbers_path = "assets\\subbers.png"
from PIL import Image, ImageDraw, ImageFont, ImageOps

def create_text_bubble(text, is_main_post, filename = "bubble_out", base_width=(720 - 2*padding)):
    # Constants for layout
    # padding = 20
    # inner_padding = 10
    # logo_size = 50
    # button_height = 30
    min_width = 300  # Minimum width of the bubble

    # Load and prepare images
    reddit_logo = Image.open(reddit_logo_path).resize((logo_size, logo_size), Image.ANTIALIAS)
    subbers = Image.open(subbers_path)
    subbers_aspect_ratio = subbers.width / subbers.height
    subbers_width = int(button_height * subbers_aspect_ratio)
    subbers = subbers.resize((subbers_width, button_height), Image.ANTIALIAS)

    # Font and text processing
    font = ImageFont.truetype(font_path, 18)
    text_lines = wrap_text(text, font, base_width - 2 * inner_padding - 2 * padding)
    max_text_width = max([font.getsize(line)[0] for line in text_lines] + [0])
    bubble_width = min(max(max_text_width + 2 * inner_padding + 2 * padding, min_width), base_width)

    # Calculate total height
    text_height = sum(font.getsize(line)[1] for line in text_lines) + (len(text_lines) - 1) * inner_padding
    content_height = logo_size + text_height + button_height + 2 * inner_padding
    total_height = content_height + 2 * padding

    # Create bubble image
    img = Image.new('RGB', (bubble_width, total_height), 'white')
    d = ImageDraw.Draw(img)

    # Place the Reddit logo and subbers image
    paste_with_transparency(img, reddit_logo, (reddit_logo_padding+2, reddit_logo_padding))
    paste_with_transparency(img, subbers, (subberLeftPadding, total_height - padding - button_height))

    # Add text centered vertically
    y_text_start = padding + logo_size + inner_padding
    for line in text_lines:
        text_width, text_height = font.getsize(line)
        text_x = (bubble_width - text_width) / 2
        d.text((text_x, y_text_start), line, fill="black", font=font)
        y_text_start += text_height + inner_padding

    # Apply rounded corners
    rounded_mask = Image.new('L', (bubble_width, total_height), 0)
    draw_rounded = ImageDraw.Draw(rounded_mask)
    draw_rounded.rounded_rectangle([(0, 0), (bubble_width, total_height)], radius=20, fill=255)
    img.putalpha(rounded_mask)

    # Save or return the image
    img_path = f"{filename}.png"
    img.save(img_path, format="PNG")
    return img_path



