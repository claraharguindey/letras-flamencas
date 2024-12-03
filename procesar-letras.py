from bs4 import BeautifulSoup
from collections import Counter
import re

EXCLUDE_WORDS = {
    "de", "lo", "qué", "ti", "ni", "tan", "has", "tus", "cómo", "o", "eso", "esa", "nos", "ese", "le", "la", "el", "y", "a", "en", "que", "con", "por", "se", "del", "las", "los",
    "un", "una", "al", "es", "para", "como", "tu", "su", "te", "me", "yo", "mi", "si", "ya", "he", "ha"
}

def process_html(html_file):
    try:
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        soup = BeautifulSoup(content, "html.parser")
        
        for tag in soup.find_all(["p", "h3"]):  # Incluimos <p> y <h3>
            style = tag.get("style", "").lower()
            if ("font-weight:bold" in style and "font-size:1.5em" in style and "text-align:center" in style) or \
               ("font:bold" in style and ".8em verdana" in style) or \
               ("text-align:center" in style and tag.name == "h3"):
                tag.decompose()

        for link in soup.find_all("a"):
            link.decompose()
        
        for numbered_tag in soup.find_all("p"):
            if re.search(r"^\d+\.", numbered_tag.get_text().strip()):
                numbered_tag.decompose()

        verses = set() 
        for p in soup.find_all("p"):
            if "font-weight:bold;" not in p.get("style", ""):  
                verses.update(p.get_text().strip().split("\n"))

        words = []
        for verse in verses:
            clean_verse = re.sub(r"[^a-záéíóúüñ\s]", "", verse.lower())
            words.extend(clean_verse.split())

        filtered_words = [word for word in words if word not in EXCLUDE_WORDS]

        count = Counter(filtered_words)

        sorted_words = count.most_common()

        with open("word_count.html", "w", encoding="utf-8") as f:
            f.write("""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Letras flamencas</title>
</head>
<body>
    <h1>Letras flamencas</h1>
    <input type="text" id="filter" placeholder="Filter words..." onkeyup="filterTable()" />
    <table id="wordTable">
        <thead>
            <tr>
                <th>Word</th>
                <th>Occurrences</th>
            </tr>
        </thead>
        <tbody>
""")
            for word, occurrences in sorted_words:
                f.write(f"            <tr><td>{word}</td><td>{occurrences}</td></tr>\n")
            
            f.write("""
        </tbody>
    </table>
    <script>
        function filterTable() {
            const filter = document.getElementById("filter").value.toLowerCase();
            const rows = document.querySelectorAll("#wordTable tbody tr");
            rows.forEach(row => {
                const word = row.cells[0].textContent.toLowerCase();
                const occurrences = row.cells[1].textContent;
                if (word.includes(filter) || occurrences.includes(filter)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            });
        }
    </script>
</body>
</html>
""")
        
        print("HTML file generated: word_count.html")
    
    except FileNotFoundError:
        print(f"The file '{html_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

html_file = "letras-flamencas.html"

process_html(html_file)
