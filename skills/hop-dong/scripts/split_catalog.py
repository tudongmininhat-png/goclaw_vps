import os
import re

input_path = "/Volumes/SSD 1TB/sanden_full/Admin_01/hop_dong/cataloge/SIV_E-Catalog_Full_VN.md"
output_dir = "/Volumes/SSD 1TB/repos skills github/goclaw_vps/skills/hop_dong/references"

os.makedirs(output_dir, exist_ok=True)

with open(input_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

current_file = None
buffer = []
file_count = 0

def save_buffer():
    global buffer, file_count, current_file
    if not buffer or not current_file:
        return
    out_path = os.path.join(output_dir, current_file)
    with open(out_path, "a", encoding="utf-8") as fout:
        fout.write("".join(buffer))
    buffer = []

for line in lines:
    if line.startswith("# TỦ ") or line.startswith("# SPB-SPE"):
        save_buffer()
        # Create a new filename based on header
        safe_name = re.sub(r'[^a-zA-Z0-9]', '-', line.strip().lower())
        safe_name = safe_name.replace('---', '-').replace('--', '-').strip('-')
        if not safe_name.endswith('.md'):
            safe_name += '.md'
        current_file = safe_name
        
    if current_file:
        buffer.append(line)

save_buffer()
print("Chia nhỏ file thành công vào folder references/")
