import os
import requests

# === CONFIGURATION ===

# 1:1 mapping: each folder updates the gist at the same index
GIST_IDS = [
    "9631643d528f73fc493be827c4d2a7c2", #ukr 
    "8b2eb266afa7afb40e3ead99b7970f87", #szl 
    "113a47ea5c95ebecc569eaf0606add83", #srbr 
    "d3ff6eb0901b2fc1f054b8f1f25c326e", #sl 
    "1f3f4cc0142f5c7b135d2f62d38bcaa5", #sk 
    "5ab0c47fc937373ec99f66e70b224cb0", #rus 
    "a2f5c4774ab6facb6e7dea4520500585", #rue 
    "908ad18962a2a67edb8340d2d2948c63", #pol 
    "95e8a56c28ff9997e6dce6ad22f07a21", #ocu 
    "b40521aaf62e6db12302251cb61e6b33", #isv 
    "6d77e5db8d489be040665e020e6a4f14", #hsb 
    "53c0364d48b833493d3471abe4ee2868", #hrv 
    "81f567de71505400033d9649d3a7b876", #dsb 
    "126763517a3582dbe33256bcc36ce3d7", #cu  
    "7385a7ad41d7345df350d17e4ef8498d", #cs 
    "6df66b9ed4f601930b4a726e04ef7379", #csb 
    "dbd96d6c2eff0a3a5a3c80f9900d82c5" #be 
    ]

FOLDER_PATHS = [
    "LibreLingo-UKR-from-EN.json",
    "LibreLingo-SZL-from-EN.json",
    "LibreLingo-SRB-from-EN.json",
    "LibreLingo-SL-from-EN.json",
    "LibreLingo-SK-from-EN.json",
    "LibreLingo-RUS-from-EN.json",
    "LibreLingo-RUE-from-EN.json",
    "LibreLingo-POL-from-EN.json",
    "LibreLingo-OCU-from-EN.json",
    "LibreLingo-ISV-from-EN.json",
    "LibreLingo-HSB-from-EN.json",
    "LibreLingo-HRV-from-EN.json",
    "LibreLingo-DSB-from-EN.json",
    "LibreLingo-CU-from-EN.json",
    "LibreLingo-CS-from-EN.json",
    "LibreLingo-CSB-from-EN.json",
    "LibreLingo-BE-from-EN.json"
]

GITHUB_TOKEN = "sd"  # With gist scope

# =======================

def read_files_from_folder(folder_path):
    files_data = {}
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        if os.path.isfile(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            files_data[filename] = {"content": content}
    return files_data

def update_gist(gist_id, token, files_data):
    url = f"https://api.github.com/gists/{gist_id}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "files": files_data
    }

    response = requests.patch(url, json=payload, headers=headers)

    if response.status_code == 200:
        print(f"✅ Gist {gist_id} updated successfully!")
        print("🔗", response.json()["html_url"])
    else:
        print(f"❌ Failed to update Gist {gist_id}: {response.status_code}")
        print(response.text)

def main():
    if len(GIST_IDS) != len(FOLDER_PATHS):
        print("❌ ERROR: GIST_IDS and FOLDER_PATHS must be the same length!")
        return

    for gist_id, folder in zip(GIST_IDS, FOLDER_PATHS):
        print(f"\n📁 Updating Gist {gist_id} with files from {folder}")
        files = read_files_from_folder("./gists/"+folder)
        if not files:
            print(f"⚠️  No files found in {folder}, skipping.")
        else:
            update_gist(gist_id, GITHUB_TOKEN, files)

if __name__ == "__main__":
    main()
