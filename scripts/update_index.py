#!/usr/bin/env python3
"""
Generate index.yml from diagrams/*.mmd frontmatter.

Now includes both normal and inverted outputs:
- svg, png
- svg_inverted, png_inverted
- image (prefers svg), image_inverted (prefers svg_inverted)
- png_scale, svg_size_bytes, png_size_bytes, svg_inverted_size_bytes, png_inverted_size_bytes
"""

import os
import re
import yaml
from glob import glob
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIAGRAMS_GLOB = os.path.join(ROOT, "diagrams", "*.mmd")
OUT_INDEX = os.path.join(ROOT, "index.yml")

def extract_frontmatter(text):
    # Try both block-comment style /* ... */ and YAML-style --- ... ---
    m = re.search(r'/\*\s*(.*?)\s*\*/', text, re.S)
    if m:
        fm = m.group(1)
        fm = re.sub(r'^\s*\*\s?', '', fm, flags=re.MULTILINE)
        return fm.strip()
    m2 = re.search(r'---\s*(.*?)\s*---', text, re.S)
    if m2:
        return m2.group(1).strip()
    return None

def safe_load_yaml(yaml_text):
    try:
        return yaml.safe_load(yaml_text) or {}
    except Exception as e:
        print(f"[warn] YAML parse error: {e}")
        return {}

def file_size_bytes(path):
    try:
        return os.path.getsize(path)
    except Exception:
        return None

def main():
    png_scale = int(os.environ.get("PNG_SCALE", "3"))
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

        rel_mmd = os.path.relpath(filepath, ROOT).replace('\\', '/')
        rel_svg = rel_mmd[:-4] + '.svg'
        rel_png = rel_mmd[:-4] + '.png'
        rel_svg_inv = rel_mmd[:-4] + '-inverted.svg'
        rel_png_inv = rel_mmd[:-4] + '-inverted.png'

        svg_exists = os.path.exists(os.path.join(ROOT, rel_svg))
        png_exists = os.path.exists(os.path.join(ROOT, rel_png))
        svg_inv_exists = os.path.exists(os.path.join(ROOT, rel_svg_inv))
        png_inv_exists = os.path.exists(os.path.join(ROOT, rel_png_inv))

        output_img = rel_svg if svg_exists else (rel_png if png_exists else None)
        output_img_inverted = rel_svg_inv if svg_inv_exists else (rel_png_inv if png_inv_exists else None)
        last_generated = data.get('last_generated') or date.today().isoformat()

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
            'svg_inverted': rel_svg_inv if svg_inv_exists else None,
            'png_inverted': rel_png_inv if png_inv_exists else None,
            'image': output_img,
            'image_inverted': output_img_inverted,
            'png_scale': png_scale,
            'svg_size_bytes': file_size_bytes(os.path.join(ROOT, rel_svg)) if svg_exists else None,
            'png_size_bytes': file_size_bytes(os.path.join(ROOT, rel_png)) if png_exists else None,
            'svg_inverted_size_bytes': file_size_bytes(os.path.join(ROOT, rel_svg_inv)) if svg_inv_exists else None,
            'png_inverted_size_bytes': file_size_bytes(os.path.join(ROOT, rel_png_inv)) if png_inv_exists else None,
        }

        entries.append(entry)

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
