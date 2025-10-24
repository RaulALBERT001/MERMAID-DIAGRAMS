#!/usr/bin/env python3
"""
Generate index.yml from diagrams/*.mmd frontmatter.

This script:
- Scans diagrams/*.mmd
- Extracts YAML-like frontmatter between /* and */
- Produces index.yml with fields including mmd, svg, png, image (prefers svg)
"""

import os
import re
import yaml
from glob import glob
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if os.path.dirname(__file__) else "."
DIAGRAMS_GLOB = os.path.join(ROOT, "diagrams", "*.mmd")
OUT_INDEX = os.path.join(ROOT, "index.yml")

def extract_frontmatter(text):
    """
    Extract block between --- and --- and return cleaned YAML text.
    """
    m = re.search(r'---\s*(.*?)\s*---', text, re.S)
    if not m:
        return None
    fm = m.group(1)
    return fm.strip()

def safe_load_yaml(yaml_text):
    try:
        return yaml.safe_load(yaml_text) or {}
    except Exception as e:
        print(f"[warn] YAML parse error: {e}")
        return {}

def main():
    entries = []
    files = sorted(glob(DIAGRAMS_GLOB))
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as fh:
                text = fh.read()
        except Exception as e:
            print(f"[error] Cannot read {filepath}: {e}")
            continue

        fm_text = extract_frontmatter(text)
        if not fm_text:
            print(f"[warn] No frontmatter found in {filepath}; skipping")
            continue

        data = safe_load_yaml(fm_text)
        if not isinstance(data, dict):
            print(f"[warn] Frontmatter in {filepath} didn't parse to dict; skipping")
            continue

        # Prepare paths relative to repo root
        rel_mmd = os.path.relpath(filepath, ROOT).replace('\\', '/')
        rel_svg = rel_mmd[:-4] + '.svg'
        rel_png = rel_mmd[:-4] + '.png'

        svg_exists = os.path.exists(os.path.join(ROOT, rel_svg))
        png_exists = os.path.exists(os.path.join(ROOT, rel_png))

        # Determine output image (prefer SVG)
        output_img = rel_svg if svg_exists else (rel_png if png_exists else None)

        # Fill defaults / fallback values
        last_generated = data.get('last_generated')
        if not last_generated:
            last_generated = date.today().isoformat()

        entry = {
            'id': data.get('id'),
            'title': data.get('title'),
            'kind': data.get('kind'),
            'area': data.get('area'),
            'version': data.get('version'),
            'tags': data.get('tags'),
            'owner': data.get('owner'),
            'ai_generator': data.get('ai_generator'),
            'prompt_file': data.get('prompt_file'),
            'prompt_hash': data.get('prompt_hash'),
            'last_generated': last_generated,
            'related_code': data.get('related_code', []),
            'mmd': rel_mmd,
            'svg': rel_svg if svg_exists else None,
            'png': rel_png if png_exists else None,
            'image': output_img
        }

        entries.append(entry)

    # Sort entries by id for stability
    entries.sort(key=lambda d: (d.get('id') or '').lower())

    output = {'diagrams': entries}
    try:
        with open(OUT_INDEX, 'w', encoding='utf-8') as out_f:
            yaml.dump(output, out_f, sort_keys=False, allow_unicode=True)
        print(f"[info] Wrote index to {OUT_INDEX} ({len(entries)} entries)")
    except Exception as e:
        print(f"[error] Failed to write index.yml: {e}")

if __name__ == "__main__":
    main()
