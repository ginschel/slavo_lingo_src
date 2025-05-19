import os
import shutil

def main():
    base_dir = os.path.abspath("to_json")
    gists_dir = os.path.join(os.path.dirname(base_dir), "gists")
    
    os.makedirs(gists_dir, exist_ok=True)

    for course_folder in os.listdir(base_dir):
        course_path = os.path.join(base_dir, course_folder)

        if os.path.isdir(course_path):
            # Create a subfolder in gists with the name of the course folder
            output_subfolder = os.path.join(gists_dir, course_folder)
            os.makedirs(output_subfolder, exist_ok=True)

            for root, _, files in os.walk(course_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, course_path)

                    flattened_path = rel_path.replace(os.sep, "___")
                    new_filename = f"librelingo___{flattened_path}"
                    dest_path = os.path.join(output_subfolder, new_filename)

                    shutil.copy2(file_path, dest_path)
                    print(f"Copied {file_path} to {dest_path}")

if __name__ == "__main__":
    main()
