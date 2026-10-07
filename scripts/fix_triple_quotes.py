def clean_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # In Python, if a string is enclosed in \"\"\", any \"\"\" inside code-str should be &quot;&quot;&quot;
    # Let's find patterns like <span class=\"code-str\">\"\"\"...\"\"\"</span>
    import re
    # Replace triple quotes inside code-str with &quot;&quot;&quot;
    cleaned = re.sub(r'<span class="code-str">"""(.*?)"""</span>', r'<span class="code-str">&quot;&quot;&quot;\1&quot;&quot;&quot;</span>', content)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(cleaned)
    print("Cleaned:", path)

clean_file("scripts/presentation_slides_part1.py")
clean_file("scripts/presentation_slides_part2.py")
