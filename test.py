import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from flask import Flask, render_template, request

app = Flask(__name__)

# --- 1. Cloudinary Configuration ---
cloudinary.config(
    cloud_name="k3ejz9zm",
    api_key="353181634129514",
    api_secret="7ZVCwDIDuAO65kFrmfYEO7VFIp0",  # ⚠️ Paste your NEW secret here
    secure=True
)

@app.route('/', methods=['GET', 'POST'])
def index():
    original_url = None
    result_url = None
    error_msg = None

    if request.method == 'POST':
        file = request.files.get('file')
        bg_color = request.form.get('bg_color', '#FFFFFF')

        if file and file.filename != '':
            try:
                # --- 2. Upload original image to Cloudinary ---
                upload_result = cloudinary.uploader.upload(file)
                public_id = upload_result['public_id']
                original_url = upload_result['secure_url']

                # --- 3. Apply background removal + new color ---
                # This builds a Cloudinary URL with the transformation:
                # e_background_removal  -> removes original background
                # b_<color>             -> sets the new background color
                result_url, _ = cloudinary_url(
                    public_id,
                    effect="background_removal",
                    background=bg_color,
                    fetch_format="auto",
                    quality="auto"
                )

            except Exception as e:
                error_msg = f"Cloudinary error: {str(e)}"

    return render_template(
        'index.html',
        original_url=original_url,
        result_url=result_url,
        error_msg=error_msg
    )

if __name__ == '__main__':
    app.run(debug=True)