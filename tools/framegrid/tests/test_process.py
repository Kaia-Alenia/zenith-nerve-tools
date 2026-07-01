import os
import shutil
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

path = "/media/alejandro/D/Pixelart/assets_pixelart"
root_dir = os.path.dirname(path) if os.path.isfile(path) else path
export_root = os.path.join(root_dir, "individual_frames")
valid_exts = (".png", ".jpg", ".jpeg", ".webp")
files = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(valid_exts)]
files.sort()
print(f"Total files: {len(files)}")

w, h = 320, 180
total_files = len(files)

for f_idx, f_path in enumerate(files):
    print(f"Processing {f_idx+1}/{total_files}: {f_path}")
    try:
        img = Image.open(f_path)
        img.load()
    except Exception as e:
        print(f"Skipping {f_path} due to error: {e}")
        continue
    img_w, img_h = img.size
    base_name = os.path.splitext(os.path.basename(f_path))[0]
    file_export_dir = os.path.join(export_root, base_name)
    
    # Do NOT actually save to avoid trashing the disk, just simulate
    # if os.path.exists(file_export_dir):
    #     shutil.rmtree(file_export_dir)
    # os.makedirs(file_export_dir, exist_ok=True)

    rows = img_h // h
    cols = img_w // w
    total_steps = rows * cols
    count = 0
    for r in range(rows):
        for c in range(cols):
            left, top = c * w, r * h
            right, bottom = left + w, top + h
            # frame = img.crop((left, top, right, bottom))
            # frame.save(os.path.join(file_export_dir, f"{count:02d}.png"))
            count += 1
            if count % 20 == 0 or count == total_steps:
                if total_files == 1:
                    p = (count / total_steps) * 100
                else:
                    p = ((f_idx + (count / total_steps)) / total_files) * 100
                # print(f"  Progress: {p:.2f}%")

print("Done")
