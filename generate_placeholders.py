from PIL import Image, ImageDraw, ImageFont
import os

images = [
    "modern-sofa.jpg",
    "sectional-sofa.jpg",
    "coffee-table.jpg",
    "dining-table.jpg",
    "armchair.jpg",
    "dining-chair.jpg"
]

output_dir = r"C:\Users\vinuv_czrvz13\Downloads\gruha-alankara\static\images\furniture"
os.makedirs(output_dir, exist_ok=True)

for img_name in images:
    if os.path.exists(os.path.join(output_dir, img_name)):
        print(f"Skipping existing image: {img_name}")
        continue
        
    img = Image.new('RGB', (400, 300), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    
    # Simple text (trying to center roughly)
    text = img_name.replace('-', ' ').replace('.jpg', '').title()
    
    # Getting default font since we can't guarantee a specific TTF file path
    # and load_default() works everywhere
    try:
        font = ImageFont.truetype("arial.ttf", size=24)
    except IOError:
        font = ImageFont.load_default()

    # Calculate text size (approximate centering for default font or specific if works)
    text_bbox = d.textbbox((0, 0), text, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    
    d.text(((400-text_w)/2, (300-text_h)/2), text, fill=(255, 255, 0), font=font)
    
    output_path = os.path.join(output_dir, img_name)
    img.save(output_path)
    print(f"Generated {output_path}")

print("Done generating placeholder images.")
