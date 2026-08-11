import os
import markdown
import subprocess

md_file = r"C:\Users\Nilesh\.gemini\antigravity-ide\brain\ba1ada1c-973c-4ccd-b0d6-c425ce26339e\fda_therapeutics_evaluation_report.md"
html_file = r"d:\Helixx\report_temp.html"
pdf_file = r"d:\Helixx\fda_therapeutics_evaluation_report.pdf"

# Read markdown
with open(md_file, "r", encoding="utf-8") as f:
    text = f.read()

# Convert to html
html_body = markdown.markdown(text, extensions=['tables'])

# CSS for a clean PDF look
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        h1 {{
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 10px;
        }}
        h2 {{
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
            margin-top: 30px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        ul {{
            margin-bottom: 20px;
        }}
        li {{
            margin-bottom: 10px;
        }}
        strong {{
            color: #000;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

# Use msedge to print to PDF
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    # Try alternative paths for Edge
    alt_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    if os.path.exists(alt_path):
        edge_path = alt_path
    else:
        print("Microsoft Edge not found. PDF generation might fail.")

print("Generating PDF...")
cmd = [
    edge_path,
    "--headless",
    "--disable-gpu",
    f"--print-to-pdf={pdf_file}",
    html_file
]

subprocess.run(cmd, check=True)
print(f"Successfully generated {pdf_file}")

# Clean up html
if os.path.exists(html_file):
    os.remove(html_file)
