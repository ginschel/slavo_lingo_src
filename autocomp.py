files = ["compile_with_dict.py","create_json_files.py","create_gist.py","upload_to_gist.py"]

for afile in files:
    with open(afile,'r', encoding='utf-8') as file:
        exec(file.read()) 