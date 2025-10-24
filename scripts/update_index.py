import re
import yaml
from glob import glob

diagrams = []
for filepath in glob("diagrams/*.mmd"):
    text = open(filepath, 'r').read()
    # Extract the block comment content between /* and */
    match = re.search(r'/\*\s*(.*?)\s*\*/', text, re.S)
    if not match:
        continue
    frontmatter = match.group(1)
    # Remove leading '*' characters from each line (YAML-like content)
    frontmatter = re.sub(r'^\s*\*\s?', '', frontmatter, flags=re.MULTILINE)
    data = yaml.safe_load(frontmatter)
    if not data:
        continue
    # Build index entry, including file paths
    entry = {
        'id': data.get('id'),
        'title': data.get('title'),
        'kind': data.get('kind'),
        'area': data.get('area'),
        'version': data.get('version'),
        'tags': data.get('tags'),
        'owner': data.get('owner'),
        'last_generated': data.get('last_generated'),
        'mmd': filepath,
        'png': filepath.replace('.mmd', '.png')
    }
    diagrams.append(entry)

# Sort or process entries if desired (e.g., by id)
diagrams.sort(key=lambda d: d.get('id') or '')

# Write to YAML index file
with open('index.yml', 'w') as f:
    yaml.dump({'diagrams': diagrams}, f, sort_keys=False)
