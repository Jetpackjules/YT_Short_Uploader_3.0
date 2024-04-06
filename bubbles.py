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
subberLeftPadding = 18
min_width = 10  # Minimum width of the bubble


reddit_logo_path = "assets\\reddit_logo.jpg"
subbers_path = "assets\\subbers.png"
# from PIL import Image, ImageDraw, ImageFont, ImageOps

def create_text_bubble(text, username, subreddit, filename="bubble_out", base_width=450, scale_factor=1.3):
    # Constants for layout
    mult = 1.6
    padding = 15
    inner_padding = 10
    logo_size = 55
    subreddit_font_size = 22  # Subreddit name font size
    username_font_size = 13  # Username font size
    username_transparency = 228  # Username text transparency (0-255)

    # Load and prepare images
    reddit_logo = Image.open(reddit_logo_path).resize((logo_size, logo_size), Image.ANTIALIAS)
    subbers = Image.open(subbers_path)
    subbers_aspect_ratio = subbers.width / subbers.height
    subbers_width = int(button_height * subbers_aspect_ratio)
    subbers = subbers.resize((subbers_width, button_height), Image.ANTIALIAS)

    # Font and text processing
    subreddit_font = ImageFont.truetype(font_path, subreddit_font_size)
    username_font = ImageFont.truetype(font_path, username_font_size)
    text_font = ImageFont.truetype(font_path, 18)

    # CUTTING OUT MORE THAN 30 WORDS FOR BREVITY (TBD IMPROVE THIS!)
    text = ' '.join(text.split()[:45])+"..." if len(text.split()) > 45 else text

    text_lines = wrap_text(text, text_font, base_width - 2 * inner_padding - logo_size - padding)
    max_text_width = max([text_font.getsize(line)[0] for line in text_lines] + [0])
    min_width = inner_padding + logo_size + padding + (logo_size + mult * padding) + (subreddit_font.getsize(subreddit)[0])
    bubble_width = int(min(max(max_text_width + 2 * inner_padding + 2 * padding, min_width), base_width))
    

    # Calculate total height
    text_height = sum(text_font.getsize(line)[1] for line in text_lines) + (len(text_lines) - 1) * inner_padding
    content_height = logo_size + text_height + 2 * inner_padding
    total_height = content_height + 2 * padding + 6

    # Create bubble image
    img = Image.new('RGB', (bubble_width, total_height), 'white')
    d = ImageDraw.Draw(img)

    # Place the Reddit logo
    paste_with_transparency(img, reddit_logo, (padding, padding))
    paste_with_transparency(img, subbers, (subberLeftPadding, total_height - button_height))


    # Add subreddit and username text next to the logo
    d.text((logo_size + mult * padding, padding + 4), "r/"+subreddit, fill="black", font=subreddit_font)
    d.text((logo_size + mult * padding, padding + subreddit_font_size + 8), username, fill=(0, 0, 0, username_transparency), font=username_font)

    # Add main text below logo, subreddit, and username
    y_text_start = padding + logo_size + inner_padding - 1
    for line in text_lines:
        text_width, text_height = text_font.getsize(line)
        text_x = padding + inner_padding - 5
        d.text((text_x, y_text_start), line, fill="black", font=text_font)
        y_text_start += text_height + 3

    # Apply rounded corners
    rounded_mask = Image.new('L', (bubble_width, total_height), 0)
    draw_rounded = ImageDraw.Draw(rounded_mask)
    draw_rounded.rounded_rectangle([(0, 0), (bubble_width, total_height)], radius=20, fill=255)
    img.putalpha(rounded_mask)

    # Scale the entire bubble by factor Y
    if scale_factor != 1.0:
        img = img.resize((int(bubble_width * scale_factor), int(total_height * scale_factor)), Image.ANTIALIAS)

    # Save or return the image
    img_path = f"output\\bubbles\\{filename}.png"
    img.save(img_path, format="PNG")
    return img_path


if __name__ == "__main__":
    create_text_bubble("THIS to say. I have 10 other things to say about this issue so I am making a very long story about this", "default_username", "AskReddit")