import os
import subprocess

COURSES_DIR = "courses"
OUTPUT_DIR = "to_json"

os.makedirs(OUTPUT_DIR, exist_ok=True)
i = 0
for entry in os.listdir(COURSES_DIR):
    path = os.path.join(COURSES_DIR, entry)
    if os.path.isdir(path):
        source = os.path.abspath(path)
        output = os.path.abspath(os.path.join(OUTPUT_DIR, f"{entry}.json"))
        print(f"{i} Exporting {entry} -> {output}")
        subprocess.run([
            "python", "-m", "librelingo_json_export.cli",
            source,
            output
        ], check=True)
        i+=1