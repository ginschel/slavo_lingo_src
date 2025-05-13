import os
import shutil
import re

def transform(text):
    text = text.strip()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r'[<>:"/\\|?*]', '_', text)
    return text

def extract_words_and_phrases(text):
    new_words_match = re.search(r"New Words:\s*\[(.*?)\]", text, re.DOTALL)
    new_words = [w.strip() for w in new_words_match.group(1).split(',')] if new_words_match else []

    phrases_match = re.search(r"Phrases:\s*\[(.*?)\]", text, re.DOTALL)
    phrases = []
    if phrases_match:
        raw = phrases_match.group(1)
        phrases = re.findall(r'"(.*?)"', raw)
    
    return new_words, phrases

def parse_english_translation_file(english_path):
    with open(english_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_words_list = []
    phrases_list = []

    pattern = re.compile(
        r"New Words:\s*\[(.*?)\]\s*|Phrases:\s*\[(.*?)\]",
        re.DOTALL
    )

    current_words = []
    current_phrases = []

    for match in pattern.finditer(content):
        words_block, phrases_block = match.groups()

        if words_block is not None:
            current_words, current_phrases = [], []
            current_words = [w.strip() for w in words_block.split(',') if w.strip()]

        elif phrases_block is not None:
            current_phrases = re.findall(r'"(.*?)"', phrases_block)
            new_words_list.append(current_words)
            phrases_list.append(current_phrases)
            current_words, current_phrases = [], []

    return new_words_list, phrases_list

def create_skill(title, id, native_words, eng_words, native_phrases, eng_phrases, source_file):
    if len(native_words) != len(eng_words):
        print(f"\n[DEBUG] New Words Mismatch in Skill '{title}' (ID {id}) from file '{source_file}':")
        print(f"Native Words ({len(native_words)}): {native_words}")
        print(f"English Words ({len(eng_words)}): {eng_words}")
        raise ValueError(f"[Error] Mismatch in NEW WORDS for skill '{title}' (ID {id}) in file '{source_file}'")

    if len(native_phrases) != len(eng_phrases):
        print(f"\n[DEBUG] Phrases Mismatch in Skill '{title}' (ID {id}) from file '{source_file}':")
        print(f"Native Phrases ({len(native_phrases)}): {native_phrases}")
        print(f"English Phrases ({len(eng_phrases)}): {eng_phrases}")
        max_len = max(len(native_phrases), len(eng_phrases))

        print(f"\n{'Index':<6} | {'Native Phrase':<30} | {'English Phrase':<30}")
        print("-" * 72)

        # Iterate through the maximum possible indices
        for i in range(max_len):
            native = native_phrases[i] if i < len(native_phrases) else ""
            english = eng_phrases[i] if i < len(eng_phrases) else ""
            print(f"{i:<6} | {native:<30} | {english:<30}")
        raise ValueError(f"[Error] Mismatch in PHRASES for skill '{title}' (ID {id}) in file '{source_file}'")

    skill_yaml = f"Skill:\n  Name: {title.strip()}\n  Id: {id}\n\n"

    skill_yaml += "New words:\n"
    for word, translation in zip(native_words, eng_words):
        skill_yaml += f"  - Word: {word}\n    Translation: {translation}\n"

    skill_yaml += "\nPhrases:\n"
    for phrase, translation in zip(native_phrases, eng_phrases):
        skill_yaml += f"  - Phrase: {phrase}\n    Translation: {translation}\n"

    return skill_yaml

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
            if os.path.isdir(course_dir):
                kurs_file = None
                gram_file = None
                for fname in os.listdir(course_dir):
                    if fname.endswith("kurs.md"):
                        kurs_file = os.path.join(course_dir, fname)
                    elif fname.endswith("gram.md"):
                        gram_file = os.path.join(course_dir, fname)
                if kurs_file and gram_file:
                    course_files.append([kurs_file, gram_file])

    root_kurs = "Interslavickurs.md"
    root_gram = "medžukurs_gramatyka.md"
    if os.path.exists(root_kurs) and os.path.exists(root_gram):
        course_files.append([root_kurs, root_gram])

    return course_files

def split_and_generate_skills(file_path, output_base_path, new_words_list, phrases_list, start_id=1):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    id_counter = start_id
    top_sections = re.split(r"(?m)^# (.+)$", content)

    for i in range(1, len(top_sections), 2):
        top_heading = top_sections[i]
        section_body = top_sections[i + 1]

        folder_name = transform(top_heading)
        module_path = os.path.join(output_base_path, folder_name)
        skills_path = os.path.join(module_path, "skills")
        os.makedirs(skills_path, exist_ok=True)

        skill_filenames = []

        sub_sections = re.split(r"(?m)^## (.+)$", section_body)
        for j in range(1, len(sub_sections), 2):
            subheading = sub_sections[j]
            subcontent = sub_sections[j + 1]

            file_name = transform(subheading) + ".yaml"
            output_path = os.path.join(skills_path, file_name)

            native_words, native_phrases = extract_words_and_phrases(subcontent)

            index = id_counter - 1
            if index >= len(new_words_list) or index >= len(phrases_list):
                raise IndexError(f"[Error] No English translation found for skill ID {id_counter}: '{subheading}' (File: {file_path})")

            eng_words = new_words_list[index]
            eng_phrases = phrases_list[index]

            skill_text = create_skill(subheading, id_counter, native_words, eng_words, native_phrases, eng_phrases, file_path)

            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(skill_text)

            skill_filenames.append(file_name)
            id_counter += 1

        # Write module.yaml
        module_yaml_path = os.path.join(module_path, "module.yaml")
        with open(module_yaml_path, "w", encoding="utf-8") as mf:
            module_name = folder_name.replace("_", " ")
            mf.write(f"Module:\n  Name: {module_name}\n\nSkills:\n")
            for fname in skill_filenames:
                mf.write(f"  - {fname}\n")

    return id_counter

def process_grammar(file_path, course_folder):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = re.split(r"(?m)^# (.+)$", content)
    for i in range(1, len(sections), 2):
        heading = sections[i]
        section_body = sections[i + 1]

        filename = transform(heading) + ".md"
        course_path = os.path.join("compiled", course_folder)

        matched_folder = None

        # Loop through all module folders and look into their 'skills' subfolder
        for module_folder in os.listdir(course_path):
            skills_path = os.path.join(course_path, module_folder, "skills")
            if not os.path.isdir(skills_path):
                continue

            yaml_path = os.path.join(skills_path, filename.replace(".md", ".yaml"))
            if os.path.exists(yaml_path):
                matched_folder = skills_path
                break

        if matched_folder:
            out_path = os.path.join(matched_folder, filename)
            with open(out_path, 'w', encoding='utf-8') as out_file:
                out_file.write(section_body.strip())
        else:
            print(f"[Warning] No matching YAML for '{filename}' in course '{course_folder}'")

def create_course(file_group, new_words_list, phrases_list):
    first_file, second_file = file_group

    if "kurs.md" in first_file:
        folder_name = os.path.basename(os.path.dirname(first_file)) if "translations" in first_file else "isv"
        language_code = folder_name.strip()
        upper_code = language_code.upper()
        course_folder_name = f"LibreLingo-{upper_code}-from-EN"

        output_dir = os.path.join("compiled", course_folder_name)
        os.makedirs(output_dir, exist_ok=True)

        id_counter = split_and_generate_skills(first_file, output_dir, new_words_list, phrases_list)
        process_grammar(second_file, course_folder_name)

        # Language name from filename
        kurs_filename = os.path.basename(first_file)
        language_name = kurs_filename.replace("kurs.md", "").replace("_", " ").strip()

        # Write course.yaml
        course_yaml_path = os.path.join(output_dir, "course.yaml")
        with open(course_yaml_path, "w", encoding="utf-8") as f:
            f.write(f"""Course:
  Language:
    Name: {language_name}
    IETF BCP 47: {language_code}
  For speakers of:
    Name: English
    IETF BCP 47: en
  License:
    Name: Attribution-ShareAlike 4.0 International
    Short name: CC BY-SA 4.0
    Link: https://creativecommons.org/licenses/by-sa/4.0/legalcode
  Repository: https://github.com/LibreLingoCommunity/LibreLingo-Isv-from-EN
  Special characters:
    - "ě"
    - "š"
    - "č"
    - "ž"
    - "Ł"

Modules:
  - Module_1_-_Very_basic_grammar_and_phrases
  - Module_2_–_Food_and_Drinks
  - Module_3_–_Learning_and_Languages
  - Module_4_–_Rooms_and_stuff_at_home
  - Module_5_–_Describing_nature_and_directions
  - Module_6_Grammar_revision
  - Module_7_–_Living_in_the_city_and_interactions_with_them
  - Module_8_Numbers_and_time_of_the_day
  - Module_9_–_Time_and_the_calendar
  - Module_10_–_Bodies,_Clothes_talking_about_people


Settings:
  Audio:
    Enabled: True
    TTS:
      - Provider: Polly
        Voice: Lucia
        Engine: standard
""")

        # Write README.md
        readme_path = os.path.join(output_dir, "README.md")
        with open(readme_path, "w", encoding="utf-8") as rf:
            rf.write(f"# LibreLingo-{upper_code}-from-EN\n\n")
            rf.write(f"{language_name} course for English Speakers that has everything a good A1 Course for a slavic language Needs, it's Long enough to get you speaking but short enough to not overwhelm you. To every new grammar concept you will get a thorough explanation. Have fun ;-)\n")

def main():
    clean_compiled_dir()
    files = get_file_paths()

    english_path = "medzukurs_english.md"
    if not os.path.exists(english_path):
        raise FileNotFoundError("[Error] English translation file 'medzukurs_english.md' not found.")

    new_words_list, phrases_list = parse_english_translation_file(english_path)

    for group in files:
        try:
            create_course(group, new_words_list, phrases_list)
        except Exception as e:
            print(f"[FATAL] Error while processing file group {group}: {e}")
            raise

if __name__ == "__main__":
    main()
