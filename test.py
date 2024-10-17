from moviepy.editor import VideoFileClip, CompositeVideoClip, vfx

# Load the main video
main_video = VideoFileClip('output/input_video.mp4')
main_duration = main_video.duration

# Load the cat video
cat_video = VideoFileClip('assets/sub_cat.webm')
cat_duration = cat_video.duration

# Remove the grey background from the cat video
# Adjust 'thr' and 's' parameters for better masking
cat_video_no_bg = cat_video.fx(vfx.mask_color, color=(204, 204, 204), thr=1, s=100 #usually 5!)

# Resize the cat video to be smaller (e.g., 25% of the main video's width)
cat_width = main_video.w * 1.75
cat_video_no_bg = cat_video_no_bg.resize(width=cat_width)

# Position the cat video at the top right corner
cat_video_no_bg = cat_video_no_bg.set_position(('center', 'top'))

# Set the start time for the cat video to overlay
start_time = main_duration - cat_duration
cat_video_no_bg = cat_video_no_bg.set_start(start_time)

# Create the composite video
final_video = CompositeVideoClip([main_video, cat_video_no_bg], size=main_video.size)

# Write the output video
final_video.write_videofile('output/final_video.mp4', codec='libx264')