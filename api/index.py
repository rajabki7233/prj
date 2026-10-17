import os
import json
import subprocess
import urllib.request
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from flask import Flask, render_template, request

app = Flask(__name__)

# --- 1. Load Configuration (Safe for Hosting & Local) ---
if os.environ.get('CLOUDINARY_SECRET'):
    # HOSTING MODE (Vercel/Render will use this)
    cloudinary.config(
        cloud_name="k3ejz9zm",
        api_key="353181634129514",
        api_secret=os.environ.get('CLOUDINARY_SECRET'),
        secure=True
    )
    FFMPEG_PATH = "ffmpeg"
else:
    # LOCAL MODE (Your computer will use this)
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        cloudinary.config(
            cloud_name=config['cloudinary']['cloud_name'],
            api_key=config['cloudinary']['api_key'],
            api_secret=config['cloudinary']['api_secret'],
            secure=True
        )
        FFMPEG_PATH = config.get('ffmpeg', {}).get('path', 'ffmpeg')
    except FileNotFoundError:
        # Fallback if config.json is missing locally
        print("WARNING: config.json not found. Please set CLOUDINARY_SECRET env variable.")
        cloudinary.config(
            cloud_name="k3ejz9zm",
            api_key="353181634129514",
            api_secret="YOUR_LOCAL_SECRET", # Hardcode here ONLY for local quick tests
            secure=True
        )
        FFMPEG_PATH = "ffmpeg"

# --- 2. Auto-description fallback ---
AUTO_DESCRIPTIONS = {
    'optimize': 'This image has been automatically optimized for the web, reducing file size while maintaining high visual quality.',
    'auto_crop': 'This image has been intelligently auto-cropped into a perfect 500x500 square, focusing automatically on the main subject.',
    'resize': 'This image has been resized to your specific dimensions while preserving the aspect ratio and visual clarity.',
    'grayscale': 'This image has been converted to a classic black and white format, giving it a timeless and dramatic look.',
    'sepia': 'This image has been treated with a warm sepia filter, creating a vintage, nostalgic, and antique photographic effect.',
    'blur': 'This image has been processed with a strong blur effect, often used to create a soft background or abstract artistic look.',
    'sharpen': 'This image has been enhanced with a sharpening filter to make edges crisper and details pop out more clearly.',
    'pixelate': 'This image has been transformed into a pixelated mosaic, creating a retro, 8-bit style digital art effect.',
    'background_removal': 'The original background of this image has been completely removed using AI, and replaced with a new solid color of your choice.',
    'cartoonify': 'This image has been transformed into a cartoon-style illustration, giving it a fun and animated look.',
    'vignette': 'A vignette effect has been applied, subtly darkening the edges to draw focus to the center of the image.',
    'oil_paint': 'This image has been rendered with an oil painting effect, giving it a textured, artistic, brush-stroke appearance.',
    'art_zorro': 'The "Zorro" artistic filter has been applied, creating a dramatic, high-contrast, black-and-white look.',
    'art_athena': 'The "Athena" artistic filter has been applied, adding a warm, golden, painterly tone to the image.',
    'art_peacock': 'The "Peacock" artistic filter has been applied, enhancing the colors with vibrant, vivid tones.',
    'art_audrey': 'The "Audrey" artistic filter has been applied, creating a soft, vintage greyscale aesthetic.'
}

@app.route('/', methods=['GET', 'POST'])
def index():
    original_url = None
    result_url = None
    video_path = None
    error_msg = None
    selected_tool = None
    final_description = None

    if request.method == 'POST':
        file = request.files.get('file')
        selected_tool = request.form.get('tool')
        bg_color = request.form.get('bg_color', '#FFFFFF')
        width = request.form.get('width')
        height = request.form.get('height')
        manual_desc = request.form.get('manual_desc', '').strip()
        use_auto_desc = request.form.get('auto_desc') == 'on'
        generate_video = request.form.get('generate_video') == 'on'

        if file and file.filename != '':
            try:
                # --- 3. Upload to Cloudinary ---
                upload_result = cloudinary.uploader.upload(file)
                public_id = upload_result['public_id']
                original_url = upload_result['secure_url']

                # --- 4. Apply Editing Tool ---
                if selected_tool == 'background_removal':
                    result_url, _ = cloudinary_url(public_id, effect="background_removal", background=bg_color, fetch_format="auto", quality="auto")
                elif selected_tool == 'grayscale':
                    result_url, _ = cloudinary_url(public_id, effect="grayscale", fetch_format="auto", quality="auto")
                elif selected_tool == 'blur':
                    result_url, _ = cloudinary_url(public_id, effect="blur:300", fetch_format="auto", quality="auto")
                elif selected_tool == 'sepia':
                    result_url, _ = cloudinary_url(public_id, effect="sepia", fetch_format="auto", quality="auto")
                elif selected_tool == 'auto_crop':
                    result_url, _ = cloudinary_url(public_id, width=500, height=500, crop="auto", gravity="auto", fetch_format="auto", quality="auto")
                elif selected_tool == 'resize':
                    resize_params = {'fetch_format': 'auto', 'quality': 'auto', 'crop': 'scale'}
                    if width and width.isdigit(): resize_params['width'] = int(width)
                    if height and height.isdigit(): resize_params['height'] = int(height)
                    if 'width' not in resize_params and 'height' not in resize_params: resize_params['width'] = 800
                    result_url, _ = cloudinary_url(public_id, **resize_params)
                elif selected_tool == 'optimize':
                    result_url, _ = cloudinary_url(public_id, fetch_format="auto", quality="auto")
                elif selected_tool == 'sharpen':
                    result_url, _ = cloudinary_url(public_id, effect="sharpen:100", fetch_format="auto", quality="auto")
                elif selected_tool == 'pixelate':
                    result_url, _ = cloudinary_url(public_id, effect="pixelate:10", fetch_format="auto", quality="auto")
                elif selected_tool == 'cartoonify':
                    result_url, _ = cloudinary_url(public_id, effect="cartoonify", fetch_format="auto", quality="auto")
                elif selected_tool == 'vignette':
                    result_url, _ = cloudinary_url(public_id, effect="vignette", fetch_format="auto", quality="auto")
                elif selected_tool == 'oil_paint':
                    result_url, _ = cloudinary_url(public_id, effect="oil_paint:60", fetch_format="auto", quality="auto")
                elif selected_tool == 'art_zorro':
                    result_url, _ = cloudinary_url(public_id, effect="art:zorro", fetch_format="auto", quality="auto")
                elif selected_tool == 'art_athena':
                    result_url, _ = cloudinary_url(public_id, effect="art:athena", fetch_format="auto", quality="auto")
                elif selected_tool == 'art_peacock':
                    result_url, _ = cloudinary_url(public_id, effect="art:peacock", fetch_format="auto", quality="auto")
                elif selected_tool == 'art_audrey':
                    result_url, _ = cloudinary_url(public_id, effect="art:audrey", fetch_format="auto", quality="auto")
                else:
                    result_url = original_url

                # --- 5. Generate Video (FFmpeg) ---
                if generate_video and result_url:
                    try:
                        # Use /tmp for Vercel compatibility, or local directory
                        temp_dir = "/tmp" if os.environ.get('VERCEL') else "."
                        local_img = os.path.join(temp_dir, f"temp_{public_id}.jpg")
                        video_filename = os.path.join(temp_dir, f"animated_{public_id}.mp4")

                        urllib.request.urlretrieve(result_url, local_img)
                        
                        cmd = [
                            FFMPEG_PATH, "-y", "-loop", "1", "-i", local_img,
                            "-vf", "zoompan=z='min(zoom+0.0015,1.15)':d=75:s=1280x720",
                            "-c:v", "libx264", "-t", "3", "-pix_fmt", "yuv420p",
                            video_filename
                        ]
                        subprocess.run(cmd, capture_output=True, check=True)

                        if os.path.exists(video_filename) and os.path.getsize(video_filename) > 0:
                            if os.environ.get('VERCEL'):
                                # Note: Serving video from Vercel /tmp requires an API route, 
                                # so we skip displaying it on Vercel to prevent crashes.
                                print("Video generated in /tmp (Vercel doesn't serve it directly).")
                            else:
                                # Local mode: Move to static folder for Flask to serve
                                os.makedirs("static", exist_ok=True)
                                final_video_path = f"static/animated_{public_id}.mp4"
                                os.rename(video_filename, final_video_path)
                                video_path = "/" + final_video_path
                        
                        # Cleanup
                        if os.path.exists(local_img):
                            os.remove(local_img)
                    except Exception as vid_err:
                        print(f"Video generation failed: {vid_err}")

                # --- 6. Description (No Gemini, just fallback) ---
                if manual_desc:
                    final_description = manual_desc
                elif use_auto_desc:
                    final_description = AUTO_DESCRIPTIONS.get(selected_tool, "No description available.")
                else:
                    final_description = "No description provided."

            except Exception as e:
                error_msg = f"Error: {str(e)}"

    return render_template(
        'index.html',
        original_url=original_url,
        result_url=result_url,
        video_path=video_path,
        error_msg=error_msg,
        selected_tool=selected_tool,
        final_description=final_description
    )

if __name__ == '__main__':
    app.run(debug=True)