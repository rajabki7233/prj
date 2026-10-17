import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from flask import Flask, render_template, request

app = Flask(__name__)

# --- 1. Cloudinary Configuration ---
cloudinary.config(
    cloud_name="k3ejz9zm",
    api_key="353181634129514",
    api_secret="7ZVCwDIDuAO65kFrmfYEO7VFIp0",  # ⚠️ REPLACE WITH NEW SECRET
    secure=True
)

# --- 2. Auto-description generator ---
AUTO_DESCRIPTIONS = {
    'optimize': 'This image has been automatically optimized for the web, reducing file size while maintaining high visual quality using auto-format and auto-quality settings.',
    'auto_crop': 'This image has been intelligently auto-cropped into a perfect 500x500 square, focusing automatically on the most important subject in the photo.',
    'resize': 'This image has been resized to your specific dimensions while preserving the aspect ratio and visual clarity.',
    'grayscale': 'This image has been converted to a classic black and white (grayscale) format, giving it a timeless and dramatic look.',
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
    error_msg = None
    selected_tool = None
    final_description = None

    if request.method == 'POST':
        file = request.files.get('file')
        selected_tool = request.form.get('tool')
        bg_color = request.form.get('bg_color', '#FFFFFF')
        
        # Resize inputs
        width = request.form.get('width')
        height = request.form.get('height')
        
        # Description inputs
        manual_desc = request.form.get('manual_desc', '').strip()
        use_auto_desc = request.form.get('auto_desc') == 'on'

        if file and file.filename != '':
            try:
                # --- 3. Upload original image ---
                upload_result = cloudinary.uploader.upload(file)
                public_id = upload_result['public_id']
                original_url = upload_result['secure_url']

                # --- 4. Apply the selected editing tool ---
                if selected_tool == 'background_removal':
                    result_url, _ = cloudinary_url(
                        public_id, effect="background_removal", background=bg_color,
                        fetch_format="auto", quality="auto"
                    )
                elif selected_tool == 'grayscale':
                    result_url, _ = cloudinary_url(
                        public_id, effect="grayscale", fetch_format="auto", quality="auto"
                    )
                elif selected_tool == 'blur':
                    result_url, _ = cloudinary_url(
                        public_id, effect="blur:300", fetch_format="auto", quality="auto"
                    )
                elif selected_tool == 'sepia':
                    result_url, _ = cloudinary_url(
                        public_id, effect="sepia", fetch_format="auto", quality="auto"
                    )
                elif selected_tool == 'auto_crop':
                    result_url, _ = cloudinary_url(
                        public_id, width=500, height=500, crop="auto", gravity="auto",
                        fetch_format="auto", quality="auto"
                    )
                elif selected_tool == 'resize':
                    resize_params = {'fetch_format': 'auto', 'quality': 'auto', 'crop': 'scale'}
                    if width and width.isdigit():
                        resize_params['width'] = int(width)
                    if height and height.isdigit():
                        resize_params['height'] = int(height)
                    if 'width' not in resize_params and 'height' not in resize_params:
                        resize_params['width'] = 800
                    result_url, _ = cloudinary_url(public_id, **resize_params)
                elif selected_tool == 'optimize':
                    result_url, _ = cloudinary_url(
                        public_id, fetch_format="auto", quality="auto"
                    )
                elif selected_tool == 'sharpen':
                    result_url, _ = cloudinary_url(
                        public_id, effect="sharpen:100", fetch_format="auto", quality="auto"
                    )
                elif selected_tool == 'pixelate':
                    result_url, _ = cloudinary_url(
                        public_id, effect="pixelate:10", fetch_format="auto", quality="auto"
                    )
                # --- NEW FREE EFFECTS ---
                elif selected_tool == 'cartoonify':
                    result_url, _ = cloudinary_url(
                        public_id, effect="cartoonify", fetch_format="auto", quality="auto"
                    )
                elif selected_tool == 'vignette':
                    result_url, _ = cloudinary_url(
                        public_id, effect="vignette", fetch_format="auto", quality="auto"
                    )
                elif selected_tool == 'oil_paint':
                    result_url, _ = cloudinary_url(
                        public_id, effect="oil_paint:60", fetch_format="auto", quality="auto"
                    )
                elif selected_tool == 'art_zorro':
                    result_url, _ = cloudinary_url(
                        public_id, effect="art:zorro", fetch_format="auto", quality="auto"
                    )
                elif selected_tool == 'art_athena':
                    result_url, _ = cloudinary_url(
                        public_id, effect="art:athena", fetch_format="auto", quality="auto"
                    )
                elif selected_tool == 'art_peacock':
                    result_url, _ = cloudinary_url(
                        public_id, effect="art:peacock", fetch_format="auto", quality="auto"
                    )
                elif selected_tool == 'art_audrey':
                    result_url, _ = cloudinary_url(
                        public_id, effect="art:audrey", fetch_format="auto", quality="auto"
                    )
                else:
                    result_url = original_url

                # --- 5. Handle Description ---
                if manual_desc:
                    final_description = manual_desc
                elif use_auto_desc:
                    final_description = AUTO_DESCRIPTIONS.get(selected_tool, "No description available.")
                else:
                    final_description = "No description provided."

            except Exception as e:
                error_msg = f"Cloudinary error: {str(e)}"

    return render_template(
        'index.html',
        original_url=original_url,
        result_url=result_url,
        error_msg=error_msg,
        selected_tool=selected_tool,
        final_description=final_description
    )

if __name__ == '__main__':
    app.run(debug=True)