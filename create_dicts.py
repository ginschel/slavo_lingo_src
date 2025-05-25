import os
import shutil
import re

def transform(text):
    """
    Transforms text into a safe filename/folder name containing only
    alphanumeric characters and converting to lowercase.
    """
    # Remove leading and trailing whitespace (optional, but good practice)
    text = text.strip()
    # Replace any character that is NOT alphanumeric (a-z, A-Z, 0-9) with nothing.
    # This removes whitespace, underscores, hyphens, spaces, special characters, etc.
    # Using '+' to collapse sequences of invalid characters into a single removal.
    text = re.sub(r'[^a-zA-Z0-9]+', '', text)
    # Convert the entire string to lowercase for consistency in filenames
    text = text.lower()
    return text

def extract_words_and_phrases(text):
    new_words_match = re.search(r"New Words:\s*\[(.*?)\]", text, re.DOTALL)
    # Ensure splitting handles potential empty strings from regex groups
    new_words = [w.strip() for w in new_words_match.group(1).split(',')] if new_words_match and new_words_match.group(1).strip() else []

    phrases_match = re.search(r"Phrases:\s*\[(.*?)\]", text, re.DOTALL)
    phrases = []
    if phrases_match:
        raw = phrases_match.group(1)
        # Extract content within quotes
        phrases = re.findall(r'"(.*?)"', raw)

    return new_words, phrases

def parse_english_translation_file(english_path):
    with open(english_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_words_list = []
    phrases_list = []

    # Pattern to find New Words and Phrases blocks sequentially
    # Use finditer to process blocks as they appear
    pattern = re.compile(
        r"New Words:\s*\[(.*?)\]\s*Phrases:\s*\[(.*?)\]",
        re.DOTALL
    )

    for match in pattern.finditer(content):
        words_block, phrases_block = match.groups()

        # Process words block - handle potential empty block
        words = [w.strip() for w in words_block.split(',') if w.strip()]

        # Process phrases block - handle potential empty block
        phrases = re.findall(r'"(.*?)"', phrases_block) if phrases_block else []

        new_words_list.append(words)
        phrases_list.append(phrases)

    return new_words_list, phrases_list


# Modified create_skill (using the new transform function is done elsewhere)
def create_skill(title, id, native_words, eng_words, native_phrases, eng_phrases, source_file):
    # Note: title here is the original subheading, not the transformed filename part
    if len(native_words) != len(eng_words):
        print(f"\n[DEBUG] New Words Mismatch in Skill '{title}' (ID {id}) from file '{source_file}':")
        print(f"Native Words ({len(native_words)}): {native_words}")
        print(f"English Words ({len(eng_words)}): {eng_words}")
        raise ValueError(f"[Error] Mismatch in NEW WORDS for skill '{title}' (ID {id}) in file '{source_file}'")

    if len(native_phrases) != len(eng_phrases):
        print(f"\n[DEBUG] Phrases Mismatch in Skill '{title}' (ID {id}) from file '{source_file}':")
        print(f"Native Phrases ({len(native_phrases)}): {native_phrases}")
        print(f"English Phrases ({len(eng_phrases)}): {eng_phrases}")
        raise ValueError(f"[Error] Mismatch in PHRASES for skill '{title}' (ID {id}) in file '{source_file}'")

    skill_yaml = f"Skill:\n  Name: {title.strip()}\n  Id: {id}\n\n"

    skill_yaml += "New words:\n"
    for word, translation in zip(native_words, eng_words):
        skill_yaml += f"  - Word: {word}\n    Translation: {translation}\n"

    skill_yaml += "\nPhrases:\n"
    for phrase, translation in zip(native_phrases, eng_phrases):
        skill_yaml += f"  - Phrase: {phrase}\n    Translation: {translation}\n"

    # --- Start of Mini-dictionary creation based on words from phrases/words ---

    def extract_unique_words_for_dict(items):
        all_words = set()

        # Regex: erkennt Wörter aus lateinischen/slawischen Buchstaben inkl. /, -, ' im Inneren
        word_regex = re.compile(
            r"[a-zA-Z\u00C0-\u017F\u0180-\u024F\u0300-\u036F\u0400-\u04FF\u0500-\u052F\u1E00-\u1EFF\u2DE0-\u2DFF\uA640-\uA69F\u1C80-\u1C8F\u1E030-\u1E08F\uFE20-\uFE2F]+(?:[’'/-][a-zA-Z\u00C0-\u017F\u0180-\u024F\u0300-\u036F\u0400-\u04FF\u0500-\u052F\u1E00-\u1EFF\u2DE0-\u2DFF\uA640-\uA69F\u1C80-\u1C8F\u1E030-\u1E08F\uFE20-\uFE2F]+)*"
        )

        for item in items:
            # Entferne Satzzeichen (aber NICHT ', -, /)
            cleaned = re.sub(r"[.,!?\"“”():;]", " ", item)
            words_in_item = word_regex.findall(cleaned)
            all_words.update(word.lower() for word in words_in_item)

        if not all_words:
            raise ValueError("No words were extracted. This may be due to unexpected input formatting.")

        return sorted(all_words)

    # Collect all unique native words for dictionary keys
    all_unique_native_words_for_dict = extract_unique_words_for_dict(native_words + native_phrases)

    # Collect all unique English words for dictionary keys
    all_unique_eng_words_for_dict = extract_unique_words_for_dict(eng_words + eng_phrases)


    skill_yaml += "\nMini-dictionary:\n"
    # Add the Belarusian words section (must be key "Belarusian")
    filename = os.path.basename(source_file)           # Get 'something.kurs.md'
    lang_name = filename.removesuffix('kurs.md')
    skill_yaml += "  "+lang_name.replace("_", " ")+":\n"
    if not all_unique_native_words_for_dict:
        print("native phrases")
        print(native_phrases)
        raise ValueError(
            f"[Error] No native words found in skill '{title}' (ID {id}) from file '{source_file}'.\n"
            "This error occurs because neither the 'New Words' nor 'Phrases' section for this skill "
            "contains any extractable words in the native language. Make sure you provided valid native words "
            "and/or phrases containing at least one alphabetic word."
        )

    for word in all_unique_native_words_for_dict:
        skill_yaml += f"    - {word}: undefined\n"
    # Add the English words section (must be key "English")
    skill_yaml += "  English:\n"
    if all_unique_eng_words_for_dict:
         for word in all_unique_eng_words_for_dict:
            skill_yaml += f"    - {word}: undefined\n"
    else:
        skill_yaml += "    # No English words or words in phrases found for dictionary\n"



    # --- End of Mini-dictionary creation ---

    return all_unique_native_words_for_dict,all_unique_eng_words_for_dict

# Rest of the functions remain largely the same, but use the new transform where appropriate

def clean_compiled_dir():
    if os.path.exists("compiled"):
        shutil.rmtree("compiled")
    os.makedirs("compiled")

def get_file_paths():
    course_files = []
    translations_path = "translations"

    if os.path.exists(translations_path):
        for entry in os.listdir(translations_path):
            course_dir = os.path.join(translations_path, entry)
            # Only process directories, and transform the directory name for the output path
            if os.path.isdir(course_dir):
                # Note: folder_name here is the ORIGINAL folder name, used to find the files
                # The TRANSFORMED name is created later in create_course for the output path
                kurs_file = None
                gram_file = None
                for fname in os.listdir(course_dir):
                    if fname.endswith("kurs.md"):
                        kurs_file = os.path.join(course_dir, fname)
                    elif fname.endswith("gram.md"):
                        gram_file = os.path.join(course_dir, fname)
                if kurs_file and gram_file:
                    # Store original paths, the transformed name is handled later
                    course_files.append([kurs_file, gram_file, os.path.basename(course_dir)])


    # Handle root files, using a fixed name for the output folder
    root_kurs = "Interslavickurs.md"
    root_gram = "medžukurs_gramatyka.md"
    if os.path.exists(root_kurs) and os.path.exists(root_gram):
        # Use a fixed output folder name like "isv" which you can decide
        course_files.append([root_kurs, root_gram, "isv"]) # Pass a source folder name component

    return course_files


def split_and_generate_skills(file_path, output_base_path, new_words_list, phrases_list, start_id=1):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    id_counter = start_id
    # Split by top-level headings
    # (?m) enables multi-line mode so ^ and $ match start/end of line
    # ^# (.+)$ matches lines starting with '# ' and captures the rest of the line as the heading
    top_sections = re.split(r"(?m)^# (.+)$", content)



    full_unique_native_words = set()
    full_unique_eng_words = set()
    # Process top-level sections (Modules)
    # The split pattern results in [text_before_first_#, heading1, text_after_heading1, heading2, ...]
    # So we iterate starting from index 1, taking steps of 2
    for i in range(1, len(top_sections), 2):
        top_heading = top_sections[i]
        section_body = top_sections[i + 1]

        # Create the module folder name using the NEW transform
        folder_name = transform(top_heading) # Will be alphanumeric lowercase
        module_path = os.path.join(output_base_path, folder_name)
        skills_path = os.path.join(module_path, "skills")
        os.makedirs(skills_path, exist_ok=True)

        skill_filenames = [] # List to store the transformed skill filenames for module.yaml



        # Split module body by subheadings (Skills)
        # ^## (.+)$ matches lines starting with '## ' and captures the rest as subheading
        sub_sections = re.split(r"(?m)^## (.+)$", section_body)
        # Process sub-sections (Skills) - similar iteration pattern
        for j in range(1, len(sub_sections), 2):
            subheading = sub_sections[j]
            subcontent = sub_sections[j + 1]

            # Create the skill file name using the NEW transform
            file_name = transform(subheading) + ".yaml" # Will be alphanumeric lowercase + .yaml
            output_path = os.path.join(skills_path, file_name)

            # Extract words and phrases from the skill content
            native_words, native_phrases = extract_words_and_phrases(subcontent)

            # Get corresponding English translations
            index = id_counter - 1
            if index >= len(new_words_list) or index >= len(phrases_list):
                 # Raise a more informative error
                 raise IndexError(f"[Error] No corresponding English translation block found for Skill ID {id_counter}: '{subheading.strip()}'\n"
                                  f"Please ensure the English translation file has a matching New Words + Phrases block for each skill heading.")


            eng_words = new_words_list[index]
            eng_phrases = phrases_list[index]

            # Create the skill YAML content
            # Pass the ORIGINAL subheading to create_skill for the Name property in YAML
            unique_native,unique_eng = create_skill(subheading, id_counter, native_words, eng_words, native_phrases, eng_phrases, file_path)
            full_unique_native_words.update(unique_native)
            full_unique_eng_words.update(unique_eng)


            # Add the transformed filename to the list for module.yaml
            skill_filenames.append(file_name)
            id_counter += 1 # Increment for the next skill

        # Write module.yaml after processing all skills in the module
        module_yaml_path = os.path.join(module_path, "module.yaml")
        with open(module_yaml_path, "w", encoding="utf-8") as mf:
            # Use the ORIGINAL top heading for the display name in module.yaml
            module_display_name = top_heading.strip()
            mf.write(f"Module:\n  Name: {module_display_name}\n\nSkills:\n") # Corrected indentation
            for fname in skill_filenames:
                mf.write(f"  - {fname}\n") # Corrected indentation

    # Return the next available ID counter
    return full_unique_native_words, full_unique_eng_words

def process_grammar(file_path, course_folder):
    # Note: course_folder here is the TRANSFORMED course folder name
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split grammar file by top-level headings
    sections = re.split(r"(?m)^# (.+)$", content)
    # Process sections (Grammar units)
    for i in range(1, len(sections), 2):
        heading = sections[i]
        section_body = sections[i + 1]

        # Create the grammar filename using the NEW transform
        filename = transform(heading) + ".md" # Will be alphanumeric lowercase + .md
        # Construct the path to the course folder using the TRANSFORMED name
        course_path = os.path.join("compiled", course_folder)

        matched_folder = None # To store the path to the matching skill directory

        # Loop through all module folders (which have TRANSFORMED names)
        for module_folder_name_transformed in os.listdir(course_path):
            # Check if it's a directory (should be the transformed module folders)
            module_path = os.path.join(course_path, module_folder_name_transformed)
            if not os.path.isdir(module_path):
                continue

            skills_path = os.path.join(module_path, "skills")
            if not os.path.isdir(skills_path):
                continue

            # Construct the expected skill YAML filename (TRANSFORMED) to find the matching folder
            # Note: The grammar heading might not match a skill subheading exactly,
            # but the transform function makes the names comparable if they started similarly.
            # We're looking for a skill YAML with a matching TRANSFORMED name.
            yaml_filename = transform(heading) + ".yaml" # Transformed grammar heading
            yaml_path = os.path.join(skills_path, yaml_filename)

            # If a skill YAML with the same transformed name exists in this skills subfolder
            if os.path.exists(yaml_path):
                matched_folder = skills_path # This is the target directory for the grammar file
                break # Found the matching skill folder, stop searching module folders

        # If a matching skill folder was found
        if matched_folder:
            # Write the grammar markdown content into the matching skill folder
            out_path = os.path.join(matched_folder, filename) # Use the transformed grammar filename
            with open(out_path, 'w', encoding='utf-8') as out_file:
                out_file.write(section_body.strip()) # Write the cleaned grammar content
        else:
            # Warning if no matching skill YAML was found for this grammar section
            print(f"[Warning] No matching skill YAML found for grammar section '{heading.strip()}' (Expected file: {filename.replace('.md', '.yaml')}) in course '{course_folder}'")
            # Optionally write the grammar file anyway to a generic location or skip it
            # For now, just prints a warning.
def extract_special_characters(file_path):
    special_chars = set()
    # Kombiniere alle relevanten Dateien
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Nimm alle Zeichen, die KEINE ASCII-Buchstaben oder Ziffern sind
        for char in content:
            if not char.isascii() or not char.isalnum():
                # Ignoriere häufige Satzzeichen und Leerzeichen
                if char not in {' ', '\n', '\t', '.', ',', ':', ';', '!', '?', '-', '(', ')', '"', "'","#","{","}","\\","&","+","/","[","]"}:
                    special_chars.add(char)
    return sorted(special_chars)


def create_course(file_group, new_words_list, phrases_list):
    first_file, second_file, source_folder_name_original = file_group

    language_code = transform(source_folder_name_original)
    upper_code = language_code.upper()
    course_folder_name = f"LibreLingo-{upper_code}-from-EN"
    output_dir = os.path.join("compiled", course_folder_name)
    os.makedirs(output_dir, exist_ok=True)

    # 🧠 Skills generieren und Wörter sammeln
    unique_native, unique_eng = split_and_generate_skills(first_file, output_dir, new_words_list, phrases_list)

    # 📄 Wörter-Dateien erzeugen
    dict_dir = os.path.join("dicts", language_code)
    os.makedirs(dict_dir, exist_ok=True)

    native_to_eng_path = os.path.join(dict_dir, language_code+"_to_en.txt")
    eng_to_native_path = os.path.join(dict_dir, "en_to_"+language_code+".txt")

    with open(native_to_eng_path, "w", encoding="utf-8") as f:
        for word in sorted(unique_native):
            f.write(f"{word}:\n")

    with open(eng_to_native_path, "w", encoding="utf-8") as f:
        for word in sorted(unique_eng):
            f.write(f"{word}:\n")


def main():
    clean_compiled_dir()
    # get_file_paths now returns [kurs_path, gram_path, source_folder_name_original]
    files_groups = get_file_paths()

    english_path = "medzukurs_english.md"
    if not os.path.exists(english_path):
         # Corrected filename in error message based on code
         raise FileNotFoundError("[Error] English translation file 'medzukurs_englisht.md' not found.")

    new_words_list, phrases_list = parse_english_translation_file(english_path)

    for file_group in files_groups:
        try:
            # create_course handles the output paths using the transformed names
            create_course(file_group, new_words_list, phrases_list)
        except Exception as e:
            # Improved error reporting to show which file group failed
            print(f"[FATAL] Error while processing file group {file_group}: {e}")
            # Depending on needs, you might want to continue processing other groups
            # pass # Use 'pass' to continue after catching error
            raise # Use 'raise' to stop execution on first error

if __name__ == "__main__":
    main()