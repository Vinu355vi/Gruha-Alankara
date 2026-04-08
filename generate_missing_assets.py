from PIL import Image, ImageDraw, ImageFont
import os

base_dir = r"C:\Users\vinuv_czrvz13\Downloads\gruha-alankara\static\images"

# Define the directory structure and files to create
structure = {
    "": ["hero-design.png"], # Root of static/images
    "steps": ["step-scan.jpg", "step-ai.jpg", "step-ar.jpg"],
    "designs": ["modern-1.jpg", "minimalist-1.jpg"],
    "users": ["user-1.jpg", "user-2.jpg", "user-3.jpg"],
    "recommendations": ["modern-sofa.jpg", "coffee-table.jpg", "floor-lamp.jpg"],
    "shop": ["sofa.jpg", "table.jpg", "chair.jpg", "art.jpg"]
}

def generate_placeholder(path, text):
    width, height = 400, 300
    if "hero" in text.lower():
        width, height = 800, 600
    elif "user" in text.lower():
        width, height = 100, 100
    
    img = Image.new('RGB', (width, height), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", size=24)
    except IOError:
        font = ImageFont.load_default()

    text = text.replace('-', ' ').replace('.jpg', '').replace('.png', '').title()
    
    # Calculate text size using textbbox
    left, top, right, bottom = d.textbbox((0, 0), text, font=font)
    text_w = right - left
    text_h = bottom - top
    
    d.text(((width - text_w) / 2, (height - text_h) / 2), text, fill=(255, 255, 0), font=font)
    
    img.save(path)
    print(f"Generated {path}")

for subdir, files in structure.items():
    target_dir = os.path.join(base_dir, subdir)
    os.makedirs(target_dir, exist_ok=True)
    
    for filename in files:
        file_path = os.path.join(target_dir, filename)
        if not os.path.exists(file_path):
            generate_placeholder(file_path, filename)
        else:
            print(f"Skipping existing: {file_path}")

print("All placeholders generated.")
