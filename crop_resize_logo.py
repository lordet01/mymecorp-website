from PIL import Image
import os

input_path = "myme_Design Asset/png/myme_landscape(primary).png"
output_path = "myme_Design Asset/png/myme_landscape(primary)_footer.png"

try:
    with Image.open(input_path) as img:
        print(f"Original size: {img.size}")
        
        # 1. 여백 타이트하게 크롭 (투명 배경 또는 흰색 배경 고려)
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        # Get bounding box of non-transparent pixels
        bbox = img.getbbox()
        
        if bbox:
            print(f"BBox found: {bbox}")
            cropped_img = img.crop(bbox)
            print(f"Cropped size: {cropped_img.size}")
            
            # 2. 2배 리사이즈
            new_width = cropped_img.width * 2
            new_height = cropped_img.height * 2
            
            resized_img = cropped_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"Resized size: {resized_img.size}")
            
            # 저장
            resized_img.save(output_path)
            print(f"Saved to: {output_path}")
        else:
            print("Image is empty or fully transparent.")

except Exception as e:
    print(f"Error: {e}")
