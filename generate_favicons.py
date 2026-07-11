from PIL import Image
import os

input_path = "myme_Design Asset/new/myMe_symbol_chrome.png"
output_dir = "myme_Design Asset/favicon"
os.makedirs(output_dir, exist_ok=True)

try:
    with Image.open(input_path) as img:
        print(f"Original size: {img.size}")
        
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # 1. favicon.ico (multi-size)
        sizes = [(16, 16), (32, 32), (48, 48)]
        img.save(f"{output_dir}/favicon.ico", format="ICO", sizes=sizes)
        print("Generated favicon.ico")

        # 2. favicon-16x16.png
        img.resize((16, 16), Image.Resampling.LANCZOS).save(f"{output_dir}/favicon-16x16.png")
        print("Generated favicon-16x16.png")
        
        # 3. favicon-32x32.png
        img.resize((32, 32), Image.Resampling.LANCZOS).save(f"{output_dir}/favicon-32x32.png")
        print("Generated favicon-32x32.png")

        # 4. apple-touch-icon.png (180x180)
        img.resize((180, 180), Image.Resampling.LANCZOS).save(f"{output_dir}/apple-touch-icon.png")
        print("Generated apple-touch-icon.png")

        # 5. android-chrome-192x192.png
        img.resize((192, 192), Image.Resampling.LANCZOS).save(f"{output_dir}/android-chrome-192x192.png")
        print("Generated android-chrome-192x192.png")

        # 6. android-chrome-512x512.png
        img.resize((512, 512), Image.Resampling.LANCZOS).save(f"{output_dir}/android-chrome-512x512.png")
        print("Generated android-chrome-512x512.png")

        print("All icons generated successfully.")

except Exception as e:
    print(f"Error: {e}")
