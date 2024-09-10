from PIL import Image, ImageDraw, ImageFont, ImageOps
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from moviepy.video.fx.all import crop
# from helper import detect_os

# font_path = ""
# os_name = detect_os()
# if os_name == 'macOS':
#     font_path = "/Library/Fonts/Arial.ttf"
# elif os_name == 'Windows':
username_font_path = "C:/Windows/Fonts/Verdana.ttf"
font_path = "C:/Windows/Fonts/Verdanab.ttf"  # Use 'arialbd.ttf' for bold Arial
# else:
#     input("FAILED TO DETECT OS!!!! ERROR!!")

def getsize_from_bbox(font, text):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

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
        while words and getsize_from_bbox(font, line + words[0])[0] <= max_width:
            line += (words.pop(0) + ' ')
        lines.append(line.strip())
    return lines

reddit_logo_path = "assets/reddit_logo.jpg"
subbers_path = "assets/subbers.png"

def create_text_bubble(text, username, subreddit, filename="bubble_out", base_width=450, video_height=1280):
    # Calculate scale factor based on video height
    scale_factor = (video_height / 1280)*1.5

    # Constants for layout (scaled)
    padding = int(15 * scale_factor-5*scale_factor)
    inner_padding = int(10 * scale_factor -1*scale_factor)
    logo_size = int(55 * scale_factor*0.88)
    subreddit_font_size = int(22 * scale_factor)
    username_font_size = int(13 * scale_factor)
    text_font_size = int(18 * scale_factor)
    button_height = int(35 * scale_factor)
    # subberLeftPadding = int(18 * scale_factor * 0.75)

    # Load and prepare images
    reddit_logo = Image.open(reddit_logo_path).resize((logo_size, logo_size), Image.LANCZOS)
    subbers = Image.open(subbers_path)
    subbers_aspect_ratio = subbers.width / subbers.height
    subbers_width = int(button_height * subbers_aspect_ratio)
    subbers = subbers.resize((subbers_width, button_height), Image.LANCZOS)

    # Font and text processing
    subreddit_font = ImageFont.truetype(font_path, subreddit_font_size)
    username_font = ImageFont.truetype(username_font_path, username_font_size)
    text_font = ImageFont.truetype(font_path, text_font_size)

    # CUTTING OUT MORE THAN 30 WORDS FOR BREVITY (TBD IMPROVE THIS!)
    text = ' '.join(text.split()[:45])+"..." if len(text.split()) > 45 else text

    scaled_base_width = int(base_width * scale_factor)
    text_lines = wrap_text(text, text_font, scaled_base_width - 2 * inner_padding - logo_size - padding)
    max_text_width = max([getsize_from_bbox(text_font, line)[0] for line in text_lines] + [0])
    min_width = inner_padding + logo_size + padding + (logo_size + 1.6 * padding) + (getsize_from_bbox(subreddit_font, subreddit)[0])
    bubble_width = int(min(max(max_text_width + 2 * inner_padding + 2 * padding, min_width), scaled_base_width))

    # Calculate total height
    text_height = sum(getsize_from_bbox(text_font, line)[1] for line in text_lines) + (len(text_lines) - 1) * inner_padding
    content_height = text_height + int((logo_size + 3.5 * inner_padding))
    total_height = int((content_height+ 2 * padding)) # + 6*(1.3)))

    # Create bubble image
    img = Image.new('RGB', (bubble_width, total_height), 'white')
    d = ImageDraw.Draw(img)

    # Place the Reddit logo
    paste_with_transparency(img, reddit_logo, (int(padding*1.4), padding))
    paste_with_transparency(img, subbers, (int(padding*1.0), int((total_height - button_height)*1.01)))

    # Add subreddit and username text next to the logo
    d.text((logo_size + int(2.0 * padding), padding + 4), "r/"+subreddit, fill="black", font=subreddit_font)
    d.text((logo_size + int(2.0 * padding), padding + subreddit_font_size + 8), username, fill=(0, 0, 0, 228), font=username_font)

    # Add main text below logo, subreddit, and username
    y_text_start = int((padding + logo_size + inner_padding )*0.95)
    for line in text_lines:
        text_width, text_height = getsize_from_bbox(text_font, line)
        text_x = padding + inner_padding - 5*scale_factor
        d.text((text_x, y_text_start), line, fill="black", font=text_font)
        y_text_start += int(text_height + 3*1.8*scale_factor)

    # Apply rounded corners
    rounded_mask = Image.new('L', (bubble_width, total_height), 0)
    draw_rounded = ImageDraw.Draw(rounded_mask)
    draw_rounded.rounded_rectangle([(0, 0), (bubble_width, total_height)], radius=int(20 * scale_factor), fill=255)
    img.putalpha(rounded_mask)

    # Save or return the image
    img_path = f"output/bubbles/{filename}.png"
    img.save(img_path, format="PNG")
    return img_path

if __name__ == "__main__":
    create_text_bubble("Im getting married! Is this not like  SUPER exciting! Great sample post, jules!", "default_username", "AskReddit", video_height=3080)  # Test with 1080p resolution