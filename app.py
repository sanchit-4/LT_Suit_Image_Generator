from flask import Flask, render_template, request
from PIL import Image, ImageDraw, ImageFont
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    """Renders the main page with the upload form."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_image():
    """Handles the image generation and displays a preview."""
    # --- 1. Get user inputs from the form ---
    logo_file = request.files.get('logo')
    main_image_file = request.files.get('main_image')
    text_input = request.form.get('text_input')
    font_size = request.form.get('font_size', 50, type=int)

    if not logo_file or not main_image_file or not text_input:
        return "Please provide all inputs.", 400

    # --- 2. Open the uploaded images ---
    logo = Image.open(logo_file.stream).convert("RGBA")
    main_image = Image.open(main_image_file.stream)

    # --- 3. Define Constants and Prepare Elements ---
    FINAL_WIDTH = 1200
    PADDING = 50
    
    # --- FIX IS HERE: Point directly to the bundled font file ---
    try:
        # This now loads the font file from your project directory
        font = ImageFont.truetype("Poppins-Regular.ttf", size=font_size)
    except IOError:
        # This fallback should now rarely, if ever, be needed
        font = ImageFont.load_default()

    # Resize logo while preserving aspect ratio
    logo_width = 300
    logo_ratio = logo_width / float(logo.width)
    logo_height = int(float(logo.height) * float(logo_ratio))
    logo = logo.resize((logo_width, logo_height))
    
    # --- 4. Calculate the size of the top section (logo + text) ---
    dummy_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    _, _, text_width, text_height = dummy_draw.multiline_textbbox((0, 0), text_input, font=font)
    top_section_height = max(logo_height, text_height) + (2 * PADDING)

    # --- 5. Resize the main image ---
    main_img_width, main_img_height = main_image.size
    scale_ratio = FINAL_WIDTH / main_img_width
    new_main_img_height = int(main_img_height * scale_ratio)
    main_image = main_image.resize((FINAL_WIDTH, new_main_img_height))
    
    # --- 6. Create the final canvas ---
    final_height = top_section_height + new_main_img_height
    canvas = Image.new('RGB', (FINAL_WIDTH, final_height), 'white')
    draw = ImageDraw.Draw(canvas)

    # --- 7. Place elements onto the canvas ---
    logo_y = (top_section_height - logo_height) // 2
    canvas.paste(logo, (PADDING, logo_y), logo)

    text_x = logo_width + (2 * PADDING)
    text_y = (top_section_height - text_height) // 2
    draw.multiline_text((text_x, text_y), text_input, fill="black", font=font)

    canvas.paste(main_image, (0, top_section_height))

    # --- 8. Save the final image to a memory buffer ---
    img_io = io.BytesIO()
    canvas.save(img_io, 'PNG')
    img_io.seek(0)
    
    # --- 9. Encode the image to Base64 and render it on the page ---
    b64_string = base64.b64encode(img_io.getvalue()).decode('utf-8')

    return render_template(
        'index.html', 
        image_data=b64_string,
        text_input=text_input,
        font_size=font_size
    )

if __name__ == '__main__':
    app.run(debug=True)