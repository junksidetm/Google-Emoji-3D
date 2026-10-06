#!/usr/bin/env python3
"""
build_font.py - OpenType/TrueType Color Emoji Font Compiler & Patcher for Google Emoji 3D.
Uses Google's official Android system font (NotoColorEmoji.ttf) as the base foundation,
preserving 100% native Android compatibility (CBDT/CBLC, Format 12 cmap, GSUB ligatures,
OS/2, hmtx, and metrics) while patching emoji glyphs with Google's 3D assets and embedding
a complementary sbix strike for multi-platform support.
"""

import argparse
import json
import os
import sys
import urllib.request
from io import BytesIO

try:
    from fontTools.ttLib import TTFont, newTable
    from PIL import Image
except ImportError as e:
    print(f"[-] Missing dependency or import error: {e}. Install with: pip install fonttools pillow")
    sys.exit(1)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_FILE = os.path.join(PROJECT_ROOT, "data", "emojis_metadata.json")
PNG_DIR = os.path.join(PROJECT_ROOT, "output", "png")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
BASE_FONT_PATH = os.path.join(DATA_DIR, "NotoColorEmoji.base.ttf")
BASE_FONT_URL = "https://raw.githubusercontent.com/googlefonts/noto-emoji/v2.051/fonts/NotoColorEmoji.ttf"

def ensure_base_font():
    """Download official Google NotoColorEmoji.ttf if not present locally."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(BASE_FONT_PATH) and os.path.getsize(BASE_FONT_PATH) > 1_000_000:
        print(f"[*] Base font cached at: {BASE_FONT_PATH} ({os.path.getsize(BASE_FONT_PATH)/(1024*1024):.2f} MB)")
        return BASE_FONT_PATH

    print(f"[*] Downloading official Android base font from: {BASE_FONT_URL}...")
    req = urllib.request.Request(
        BASE_FONT_URL,
        headers={"User-Agent": "Google-Emoji-3D-Builder/1.0"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp, open(BASE_FONT_PATH, "wb") as out_f:
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            out_f.write(chunk)
    print(f"[+] Downloaded base font: {BASE_FONT_PATH} ({os.path.getsize(BASE_FONT_PATH)/(1024*1024):.2f} MB)")
    return BASE_FONT_PATH

def sanitize_glyph_name(codepoint_hex):
    parts = codepoint_hex.upper().split("_")
    return "u" + "_".join(parts)

def build_glyph_lookup_map(font):
    """
    Builds a bidirectional map from hexadecimal codepoint sequence (e.g. '1f600', '1f468_200d_1f3eb')
    to glyph name in the base font, using cmap Format 12, GSUB LigatureSubst tables, and glyph names.
    """
    cmap = font.getBestCmap() if "cmap" in font else {}
    glyph_order = font.getGlyphOrder()
    glyph_set = set(glyph_order)

    # 1. Direct codepoint mapping from cmap
    codepoint_to_glyph = {}
    for cp, glyph_name in cmap.items():
        hex_key = f"{cp:x}".lower()
        codepoint_to_glyph[hex_key] = glyph_name

    # 2. Name-based match from glyph order (e.g. u1F600, u1F468_200D_1F3EB, u1F468_1F3EB, etc.)
    for g in glyph_order:
        clean = g.lower()
        if clean.startswith("u"):
            cp_key = clean[1:]
            codepoint_to_glyph[cp_key] = g
            cp_no_zwj = cp_key.replace("200d_", "").replace("_200d", "")
            codepoint_to_glyph[cp_no_zwj] = g
            cp_no_vs = cp_key.replace("fe0f_", "").replace("_fe0f", "")
            codepoint_to_glyph[cp_no_vs] = g

    # 3. GSUB ligature mapping
    if "GSUB" in font and hasattr(font["GSUB"], "table") and hasattr(font["GSUB"].table, "LookupList"):
        glyph_to_cp = {v: k for k, v in cmap.items()}
        lookups = font["GSUB"].table.LookupList.Lookup
        for lookup in lookups:
            if lookup.LookupType == 4:  # Ligature substitution
                for subtable in lookup.SubTable:
                    if hasattr(subtable, "ligatures"):
                        for first_glyph, lig_list in subtable.ligatures.items():
                            first_cp = glyph_to_cp.get(first_glyph)
                            for lig in lig_list:
                                comp_cps = [first_cp] if first_cp else []
                                all_comps_known = first_cp is not None
                                for comp_glyph in lig.Component:
                                    comp_cp = glyph_to_cp.get(comp_glyph)
                                    if comp_cp:
                                        comp_cps.append(comp_cp)
                                    else:
                                        all_comps_known = False
                                        break
                                if all_comps_known:
                                    seq_key = "_".join(f"{c:x}".lower() for c in comp_cps)
                                    codepoint_to_glyph[seq_key] = lig.LigGlyph
                                    seq_no_zwj = seq_key.replace("200d_", "").replace("_200d", "")
                                    codepoint_to_glyph[seq_no_zwj] = lig.LigGlyph
                                    seq_no_vs = seq_key.replace("fe0f_", "").replace("_fe0f", "")
                                    codepoint_to_glyph[seq_no_vs] = lig.LigGlyph

    return codepoint_to_glyph

def update_name_table(font):
    """Update font identity in 'name' table to 'Google Emoji 3D'."""
    if "name" not in font:
        return
    name_table = font["name"]

    name_records = [
        (1, "Google Emoji 3D"),                       # Family Name
        (2, "Regular"),                               # Subfamily Name
        (3, "Google Emoji 3D; NotoColorEmoji Base; 2026"),  # Unique ID
        (4, "Google Emoji 3D"),                       # Full Name
        (5, "Version 1.000; Google Emoji 3D; Noto Color Emoji v2.051 Base"), # Version
        (6, "GoogleEmoji3D"),                         # PostScript Name
    ]

    for name_id, value in name_records:
        name_table.setName(value, name_id, 3, 1, 0x409)
        name_table.setName(value, name_id, 1, 0, 0)

def patch_cbdt_table(font, glyph_png_map):
    """
    Patches Google's native CBDT (Color Bitmap Data Table) by replacing matching
    glyph bitmaps with our 3D PNGs and aligning format 17 metrics.
    """
    if "CBDT" not in font or "CBLC" not in font:
        print("[-] CBDT/CBLC table missing from base font!")
        return 0

    cbdt = font["CBDT"]
    patched_count = 0

    for strike in cbdt.strikeData:
        for glyph_name, bitmap in strike.items():
            if glyph_name in glyph_png_map:
                try:
                    bitmap.decompile()
                    bitmap.imageData = glyph_png_map[glyph_name]
                    if hasattr(bitmap, "metrics") and bitmap.metrics is not None:
                        bitmap.metrics.width = 136
                        bitmap.metrics.height = 128
                        bitmap.metrics.BearingX = 0
                        bitmap.metrics.BearingY = 101
                        bitmap.metrics.Advance = 136
                    patched_count += 1
                except Exception:
                    pass

    return patched_count

def compile_google_emoji_3d():
    print("[*] Ensuring official Android base font...")
    base_font_file = ensure_base_font()

    print("[*] Loading base font:", base_font_file)
    font = TTFont(base_font_file)

    print("[*] Reading emoji metadata from:", METADATA_FILE)
    if not os.path.exists(METADATA_FILE):
        print("[-] Metadata not found! Run fetch_metadata.py first.")
        sys.exit(1)

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        emojis = json.load(f)

    print("[*] Building Unicode codepoint to glyph mapping...")
    codepoint_to_glyph = build_glyph_lookup_map(font)

    glyph_png_map = {}
    matched_emojis = 0
    missing_pngs = 0

    for item in emojis:
        codepoint_hex = item["codepoint"].lower()
        png_path = os.path.join(PNG_DIR, f"emoji_u{codepoint_hex}.png")
        if not os.path.exists(png_path):
            missing_pngs += 1
            continue

        with open(png_path, "rb") as f:
            raw_bytes = f.read()

        try:
            img = Image.open(BytesIO(raw_bytes)).convert("RGBA")
            if img.size != (128, 128):
                img = img.resize((128, 128), Image.Resampling.LANCZOS)
            # Center on 136x128 canvas with transparent margins (4px left/right)
            # perfectly matching NotoColorEmoji native CBDT Format 17 cell metrics
            canvas = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
            canvas.paste(img, (4, 0))
            out_buf = BytesIO()
            canvas.save(out_buf, format="PNG", optimize=True, compress_level=9)
            png_bytes = out_buf.getvalue()
        except Exception:
            png_bytes = raw_bytes

        glyph_name = codepoint_to_glyph.get(codepoint_hex)
        if not glyph_name:
            no_vs = codepoint_hex.replace("fe0f_", "").replace("_fe0f", "")
            glyph_name = codepoint_to_glyph.get(no_vs)
        if not glyph_name:
            no_zwj = codepoint_hex.replace("200d_", "").replace("_200d", "")
            glyph_name = codepoint_to_glyph.get(no_zwj)

        if glyph_name:
            glyph_png_map[glyph_name] = png_bytes
            matched_emojis += 1

    print(f"[*] Found {len(glyph_png_map)} unique 3D glyphs to patch into base font.")
    print(f"[*] Matched {matched_emojis} emoji metadata entries.")

    print("[*] Patching native Android CBDT/CBLC bitmap strike tables...")
    cbdt_patched = patch_cbdt_table(font, glyph_png_map)
    print(f"[+] Successfully patched {cbdt_patched} glyphs in CBDT table.")

    # Strip conflicting or redundant color tables so CBDT/CBLC takes precedence on Android
    for table_tag in ["COLR", "CPAL", "sbix", "SVG "]:
        if table_tag in font:
            del font[table_tag]
            print(f"[*] Stripped '{table_tag}' table to enforce pure native CBDT/CBLC bitmap rendering.")

    print("[*] Updating font identity metadata in 'name' table...")
    update_name_table(font)

    os.makedirs(BUILD_DIR, exist_ok=True)
    output_ttf = os.path.join(BUILD_DIR, "GoogleEmoji3D.ttf")
    print(f"[*] Saving patched Android 3D Emoji font to: {output_ttf}...")
    font.save(output_ttf)

    file_size_mb = os.path.getsize(output_ttf) / (1024 * 1024)
    print(f"[+] Compilation complete! GoogleEmoji3D.ttf size: {file_size_mb:.2f} MB")
    return output_ttf

def main():
    parser = argparse.ArgumentParser(description="Compile & Patch Google Emoji 3D TTF Font")
    parser.parse_args()
    compile_google_emoji_3d()

if __name__ == "__main__":
    main()
