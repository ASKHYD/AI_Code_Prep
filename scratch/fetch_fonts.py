import io
import os
import tarfile
import urllib.request

FONTS = [
    {
        "name": "fraunces",
        "url": "https://registry.npmjs.org/@fontsource/fraunces/-/fraunces-5.3.0.tgz",
        "version": "5.3.0",
        "weights": ["500", "600", "700", "800"],
    },
    {
        "name": "inter",
        "url": "https://registry.npmjs.org/@fontsource/inter/-/inter-5.3.0.tgz",
        "version": "5.3.0",
        "weights": ["400", "500", "600", "700"],
    },
    {
        "name": "jetbrains-mono",
        "url": "https://registry.npmjs.org/@fontsource/jetbrains-mono/-/jetbrains-mono-5.3.0.tgz",
        "version": "5.3.0",
        "weights": ["400", "500", "600", "700"],
    },
]

out_dir = os.path.abspath("assets/fonts")
os.makedirs(out_dir, exist_ok=True)

inventory = []

for font in FONTS:
    print(f"Downloading {font['name']} v{font['version']}...")
    req = urllib.request.Request(font["url"], headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        tar_bytes = resp.read()

    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:gz") as tar:
        for weight in font["weights"]:
            target_name = f"package/files/{font['name']}-latin-{weight}-normal.woff2"
            try:
                member = tar.getmember(target_name)
            except KeyError:
                print(f"ERROR: could not find {target_name}")
                continue

            extracted_file = tar.extractfile(member)
            content = extracted_file.read()
            out_filename = f"{font['name']}-latin-{weight}-normal.woff2"
            dest_path = os.path.join(out_dir, out_filename)
            with open(dest_path, "wb") as f:
                f.write(content)

            # Check WOFF2 magic bytes
            is_valid_woff2 = content[:4] == b"wOF2"
            inventory.append({
                "file": out_filename,
                "size": len(content),
                "valid": is_valid_woff2,
                "pkg": f"@fontsource/{font['name']}@{font['version']}"
            })

print("\n--- EXTRACTION COMPLETE ---")
for item in inventory:
    status = "VALID WOFF2" if item["valid"] else "INVALID"
    print(f"{item['file']:40} {item['size']:>7} bytes   {status}   ({item['pkg']})")

