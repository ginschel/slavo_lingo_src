original_headings = [
    "# Conjugation of to be and the Nominative Case",
    "# Greetings & Phrases for conversations",
    "# Family (Instrumental case)",
    "# Hobbies (Verbs – Imperfective only)",
    "# Sports (very basic accusative case + very basic locative)",
    "# Food (Accusative case)",
    "# Drinks (Genitive case)",
    "# Fruits",
    "# Studying & Writing (Locative case)",
    "# Shapes",
    "# Nationalities / Languages",
    "# Rooms/furniture",
    "# Stuff in the kitchen",
    "# Animals (Dative case)",
    "# Nature",
    "# Weather",
    "# Colours",
    "# Cardinal points/directions",
    "# Grammar revision cases",
    "# Grammar revision pronouncs",
    "# City/Buildings",
    "# Professions",
    "# Transport/Vehicles/Car",
    "# Buying in the Shop",
    "# Asking for Directions",
    "# Numbers 0-10",
    "# Numbers 11-20",
    "# Numbers 10-100",
    "# Numbers 100-1000",
    "# Ordinal Numbers",
    "# Talking about Time (past tense)",
    "# Weekdays/Months",
    "# Seasons of the year (future tense)",
    "# Clothes  (basic conjunctions)",
    "# Body",
    "# Character (Conditional)",
    "# Emotions (adverbs)",
    "# Physical Appearance (Easy comparisons)"
]

replacement_headings = [
    "# Conjugation of to be",
    "# Greetings & Phrases",
    "# Family",
    "# Hobbies",
    "# Sports",
    "# Food",
    "# Drinks",
    "# Fruits",
    "# Studying & Writing",
    "# Shapes",
    "# Nationalities",
    "# Rooms/furniture",
    "# Stuff in the kitchen",
    "# Animals",
    "# Nature",
    "# Weather",
    "# Colours",
    "# Cardinal points",
    "# Cases revision",
    "# Pronouns revision",
    "# City/Buildings",
    "# Professions",
    "# Transport/Vehicles/Car",
    "# Buying in the Shop",
    "# Asking for Directions",
    "# Numbers 0-10",
    "# Numbers 11-20",
    "# Numbers 10-100",
    "# Numbers 100-1000",
    "# Ordinal Numbers",
    "# Talking about Time",
    "# Weekdays/Months",
    "# Seasons of the year",
    "# Clothes",
    "# Body",
    "# Character",
    "# Emotions",
    "# Physical Appearance"
]


import os

def replace_headings_in_files(root_dir, originals, replacements):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".md"):
                filepath = os.path.join(dirpath, filename)
                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.readlines()

                changed = False
                new_content = []

                for line in content:
                    new_line = line
                    for orig, repl in zip(originals, replacements):
                        # Kurs file: look for ## heading, replace with same +#
                        if filename.endswith("kurs.md"):
                            kurs_orig = "#" + orig  # search for ##Heading
                            kurs_repl = "#" + repl  # replace with ##NewHeading
                            if kurs_orig in new_line:
                                new_line = new_line.replace(kurs_orig, kurs_repl)
                                print(f"[kurs.md] Replaced in {filepath}: '{kurs_orig}' -> '{kurs_repl}'")
                                changed = True
                        else:
                            if orig in new_line:
                                new_line = new_line.replace(orig, repl)
                                print(f"[other.md] Replaced in {filepath}: '{orig}' -> '{repl}'")
                                changed = True
                    new_content.append(new_line)

                if changed:
                    with open(filepath, "w", encoding="utf-8") as file:
                        file.writelines(new_content)

# Usage example:
if __name__ == "__main__":
    root_path = "."  # Update this to your folder
    replace_headings_in_files(root_path, original_headings, replacement_headings)