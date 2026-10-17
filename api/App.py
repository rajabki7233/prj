import os
import subprocess
import urllib.request
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from flask import Flask, render_template, request
from google import genai
from google.genai import types

app = Flask(__name__)

# --- 1. Configuration for Vercel ---
# Vercel will inject these from your Environment Variables settings
cloudinary.config(
    cloud_name="k3ejz9zm",
    api_key="353181634129514",
    api_secret=os.environ.get('CLOUDINARY_SECRET', 'fallback_secret_if_local'),
    secure=True
)

# Initialize Gemini
gemini_key = os.environ.get('GEMINI_API_KEY')
if gemini_key:
    os.environ["GEMINI_API_KEY"] = gemini_key
    client = genai.Client()

# --- 2. Auto-description fallback ---
AUTO_DESCRIPTIONS = {
    'optimize': 'This image has been automatically optimized for the web...',
    'auto_crop': 'This image has been intelligently auto-cropped...',
    'resize': 'This image has been resized to your specific dimensions...',
    'grayscale': 'This image has been converted to a classic black and white format...',
    'sepia': 'This image has been treated with a warm sepia filter...',
    'blur': 'This image has been processed with a strong blur effect...',
    'sharpen': 'This image has been enhanced with a sharpening filter...',
    'pixelate': 'This image has been transformed into a pixelated mosaic...',
    'background_removal': 'The original background has been removed and replaced...',
    'cartoonify': 'This image has been transformed into a cartoon-style illustration...',
    'vignette': 'A vignette effect has been applied...',
    'oil_paint': 'This image has been rendered with an oil painting effect...',
    'art_zorro': 'The "Zorro" artistic filter has been applied...',
    'art_athena': 'The "Athena" artistic filter has been applied...',
    'art_peacock': 'The "Peacock" artistic filter has been applied...',
    'art_audrey': 'The "Audrey" artistic filter has been applied...'
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
                file_bytes = file.read()
                file.seek(0)
                mime_type = file.mimetype or "image/jpeg"

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

                # --- 5. Generate Video (Safely caught for Vercel) ---
                if generate_video and result_url:
                    try:
                        local_img = f"/tmp/temp_{public_id}.jpg" # Vercel allows writing to /tmp
                        urllib.request.urlretrieve(result_url, local_img)
                        
                        video_filename = f"/tmp/animated_{public_id}.mp4"

                        cmd = [
                            "ffmpeg", "-y", "-loop", "1", "-i", local_img,
                            "-vf", "zoompan=z='min(zoom+0.0015,1.15)':d=75:s=1280x720",
                            "-c:v", "libx264", "-t", "3", "-pix_fmt", "yuv420p",
                            video_filename
                        ]
                        subprocess.run(cmd, capture_output=True, check=True)
                        
                        # Note: Serving videos from Vercel /tmp requires a different setup, 
                        # so we will just skip showing the video on the live site to prevent crashes.
                        pass 
                    except Exception as vid_err:
                        print(f"Video generation failed (Expected on Vercel): {vid_err}")

                # --- 6. Description ---
                if manual_desc:
                    final_description = manual_desc
                elif use_auto_desc and gemini_key:
                    try:
                        prompt = (
                            f"You are an expert image analyst. Look at this image carefully. "
                            f"The user has applied the '{selected_tool}' effect to it. "
                            f"Write a detailed, engaging paragraph (3-4 sentences) describing: "
                            f"1. The main subjects and objects. "
                            f"2. The setting and environment. "
                            f"3. The mood, lighting, and colors. "
                            f"4. How the '{selected_tool}' effect changes the overall feel."
                        )
                        gemini_response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[
                                types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                                prompt
                            ]
                        )
                        final_description = gemini_response.text.strip()
                    except Exception as gemini_err:
                        print(f"Gemini error: {gemini_err}")
                        final_description = AUTO_DESCRIPTIONS.get(selected_tool, "No description available.")
                else:
                    final_description = AUTO_DESCRIPTIONS.get(selected_tool, "No description provided.")

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