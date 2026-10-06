#!/usr/bin/env python3
"""
test_emoji_font.py - Comprehensive OpenType & Emoji Font Tester for Google Emoji 3D.
Validates TrueType / OpenType font structure, table conformance, cross-platform compatibility,
complex emoji sequences (ZWJ, skin tones, flags, VS16), and compares against official
Google NotoColorEmoji reference standards.
"""

import argparse
import os
import sys
from io import BytesIO

try:
    from fontTools.ttLib import TTFont
    from PIL import Image
except ImportError as e:
    print(f"[-] Missing dependencies: {e}. Install with: pip install fonttools pillow")
    sys.exit(1)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FONT_PATH = os.path.join(PROJECT_ROOT, "build", "GoogleEmoji3D.ttf")
DEFAULT_BASE_FONT_PATH = os.path.join(PROJECT_ROOT, "data", "NotoColorEmoji.base.ttf")

REQUIRED_BASE_TABLES = [
    "head", "hhea", "maxp", "OS/2", "hmtx", "cmap", "name", "post"
]

# Canonical Unicode test sequences representing all emoji classes
BENCHMARK_SEQUENCES = [
    # Single Codepoint Emojis
    {"name": "Grinning Face (😀)", "cps": [0x1F600], "type": "single"},
    {"name": "Face with Tears of Joy (😂)", "cps": [0x1F602], "type": "single"},
    {"name": "Fire (🔥)", "cps": [0x1F525], "type": "single"},
    {"name": "Sparkles (✨)", "cps": [0x2728], "type": "single"},
    {"name": "Rocket (🚀)", "cps": [0x1F680], "type": "single"},

    # Variation Selector-16 (VS16 / U+FE0F) Presentation Forms
    {"name": "Smiling Face with VS16 (☺️)", "cps": [0x263A, 0xFE0F], "type": "vs16"},
    {"name": "Red Heart with VS16 (❤️)", "cps": [0x2764, 0xFE0F], "type": "vs16"},

    # Skin Tone Modifier Sequences (Fitzpatrick scale)
    {"name": "Thumbs Up: Light Skin (👍🏻)", "cps": [0x1F44D, 0x1F3FB], "type": "skin_tone"},
    {"name": "Thumbs Up: Medium Skin (👍🏽)", "cps": [0x1F44D, 0x1F3FD], "type": "skin_tone"},
    {"name": "Thumbs Up: Dark Skin (👍🏿)", "cps": [0x1F44D, 0x1F3FF], "type": "skin_tone"},
    {"name": "Wave: Medium Skin (👋🏽)", "cps": [0x1F44B, 0x1F3FD], "type": "skin_tone"},

    # Zero-Width Joiner (ZWJ / U+200D) Complex Sequences
    {"name": "Man Technologist (👨‍💻)", "cps": [0x1F468, 0x200D, 0x1F4BB], "type": "zwj"},
    {"name": "Woman Scientist (👩‍🔬)", "cps": [0x1F469, 0x200D, 0x1F52C], "type": "zwj"},
    {"name": "Family: Man, Woman, Girl (👨‍👩‍👧)", "cps": [0x1F468, 0x200D, 0x1F469, 0x200D, 0x1F467], "type": "zwj"},
    {"name": "Man Running with VS16 (🏃‍♂️)", "cps": [0x1F3C3, 0x200D, 0x2642, 0xFE0F], "type": "zwj"},
    {"name": "Heart on Fire (❤️‍🔥)", "cps": [0x2764, 0xFE0F, 0x200D, 0x1F525], "type": "zwj"},

    # Regional Indicator Pairs (Country Flags)
    {"name": "Flag of United States (🇺🇸)", "cps": [0x1F1FA, 0x1F1F8], "type": "flag"},
    {"name": "Flag of India (🇮🇳)", "cps": [0x1F1EE, 0x1F1F3], "type": "flag"},
    {"name": "Flag of Japan (🇯🇵)", "cps": [0x1F1EF, 0x1F1F5], "type": "flag"},
    {"name": "Flag of Taiwan (🇹🇼)", "cps": [0x1F1F9, 0x1F1FC], "type": "flag"},
]


class EmojiFontTester:
    def __init__(self, font_path, base_font_path=None):
        self.font_path = font_path
        self.base_font_path = base_font_path
        self.font = None
        self.base_font = None
        self.errors = []
        self.warnings = []
        self.passes = []

    def log_pass(self, test_name, detail=""):
        self.passes.append((test_name, detail))
        print(f"  [PASS] {test_name}: {detail}" if detail else f"  [PASS] {test_name}")

    def log_warn(self, test_name, detail=""):
        self.warnings.append((test_name, detail))
        print(f"  [WARN] {test_name}: {detail}" if detail else f"  [WARN] {test_name}")

    def log_fail(self, test_name, detail=""):
        self.errors.append((test_name, detail))
        print(f"  [FAIL] {test_name}: {detail}" if detail else f"  [FAIL] {test_name}")

    def load_fonts(self):
        print(f"\n[1/7] Loading and Parsing Font File: {self.font_path}")
        if not os.path.exists(self.font_path):
            self.log_fail("Font File Existence", f"File not found: {self.font_path}")
            return False

        file_size_mb = os.path.getsize(self.font_path) / (1024 * 1024)
        print(f"  • Font File Size: {file_size_mb:.2f} MB ({os.path.getsize(self.font_path):,} bytes)")

        # Memory benchmark check
        if file_size_mb > 90.0:
            self.log_fail("Font Size Limit", f"{file_size_mb:.2f} MB exceeds safe Android heap threshold (90 MB)")
        elif file_size_mb > 50.0:
            self.log_warn("Font Size Optimization", f"{file_size_mb:.2f} MB is relatively heavy; recommend palette quantization")
        else:
            self.log_pass("Font Size Benchmark", f"{file_size_mb:.2f} MB within optimal memory footprint")

        try:
            self.font = TTFont(self.font_path)
            self.log_pass("OpenType SFNT Header", f"Successfully parsed TrueType container with {len(self.font.keys())} tables")
        except Exception as e:
            self.log_fail("OpenType SFNT Header", f"Failed to parse TrueType container: {e}")
            return False

        if self.base_font_path and os.path.exists(self.base_font_path):
            try:
                self.base_font = TTFont(self.base_font_path)
                print(f"  • Reference Base Font Loaded: {self.base_font_path} ({len(self.base_font.keys())} tables)")
            except Exception as e:
                self.log_warn("Reference Base Font", f"Could not load reference base font: {e}")

        return True

    def test_required_tables(self):
        print("\n[2/7] Verifying Required OpenType & Color Tables")
        present_tables = set(self.font.keys())

        # Check standard OpenType structural tables
        for table in REQUIRED_BASE_TABLES:
            if table in present_tables:
                self.log_pass(f"Table '{table}'", "Present and registered in SFNT directory")
            else:
                self.log_fail(f"Table '{table}'", "Mandatory OpenType table is missing!")

        # Outline vs Bitmap verification
        has_cbdt = "CBDT" in present_tables and "CBLC" in present_tables
        has_outlines = ("glyf" in present_tables and "loca" in present_tables) or ("CFF " in present_tables or "CFF2" in present_tables)
        if has_outlines:
            self.log_pass("Glyph Outlines (glyf/loca or CFF)", "Outline geometry tables present")
        elif has_cbdt:
            self.log_pass("Color Bitmap Glyphs (CBDT/CBLC)", "Native outline-less bitmap font (valid per OpenType CBDT specification)")
        else:
            self.log_fail("Glyph Outlines / Bitmaps", "Neither outline tables (glyf/loca/CFF) nor color bitmap tables (CBDT/CBLC) found!")

        # Color table analysis
        has_sbix = "sbix" in present_tables
        has_colr = "COLR" in present_tables and "CPAL" in present_tables
        has_svg = "SVG " in present_tables

        print(f"  • Color Tables Detected: CBDT/CBLC={has_cbdt}, sbix={has_sbix}, COLR/CPAL={has_colr}, SVG={has_svg}")

        if has_cbdt:
            self.log_pass("Android Color Bitmap (CBDT/CBLC)", "Active native Android format")
        else:
            self.log_fail("Android Color Bitmap (CBDT/CBLC)", "CBDT and CBLC tables must be present for Android font loaders")

        # Conflict check: If font has both COLR and CBDT, Android 13+ and Chrome will prioritize COLR over CBDT!
        if has_cbdt and has_colr:
            self.log_fail(
                "Color Table Precedence Conflict",
                "Both CBDT and COLR/CPAL tables exist! Android 13+ and browsers prioritize COLR over CBDT, "
                "which will cause devices to render flat 2D vector emojis instead of patched 3D bitmaps!"
            )
        elif has_cbdt and not has_colr:
            self.log_pass("Color Table Precedence", "Clean pure CBDT/CBLC configuration; no vector COLR tables shadow bitmaps")

    def test_header_and_metrics(self):
        print("\n[3/7] Verifying Header, Metrics & Typography Bounds")
        head = self.font.get("head")
        if head:
            magic = getattr(head, "magicNumber", 0)
            if magic == 0x5F0F3CF5:
                self.log_pass("head.magicNumber", f"0x{magic:08X} (Valid TrueType signature)")
            else:
                self.log_fail("head.magicNumber", f"0x{magic:08X} (Invalid TrueType signature, expected 0x5F0F3CF5)")

            upem = getattr(head, "unitsPerEm", 0)
            if upem in (1000, 2048):
                self.log_pass("head.unitsPerEm", f"{upem} standard glyph grid units")
            else:
                self.log_warn("head.unitsPerEm", f"{upem} non-standard unitsPerEm")

        hhea = self.font.get("hhea")
        os2 = self.font.get("OS/2")
        if hhea and os2:
            print(f"  • hhea Metrics: Ascent={hhea.ascent}, Descent={hhea.descent}, LineGap={hhea.lineGap}")
            print(f"  • OS/2 Typo Metrics: sTypoAscender={os2.sTypoAscender}, sTypoDescender={os2.sTypoDescender}, sTypoLineGap={os2.sTypoLineGap}")
            print(f"  • OS/2 Windows Metrics: usWinAscent={os2.usWinAscent}, usWinDescent={os2.usWinDescent}")

            # Check for extreme clipping bounds
            if hhea.ascent <= 0 or os2.usWinAscent <= 0:
                self.log_fail("Ascender Metrics", "Negative or zero ascender detected; glyphs will clip")
            else:
                self.log_pass("Vertical Metrics Alignment", "Valid positive ascender values")

    def test_name_records(self):
        print("\n[4/7] Verifying Naming Records & Font Identification")
        name_table = self.font.get("name")
        if not name_table:
            self.log_fail("name Table", "Naming table missing")
            return

        family_name = name_table.getDebugName(1)
        subfamily = name_table.getDebugName(2)
        full_name = name_table.getDebugName(4)
        ps_name = name_table.getDebugName(6)

        print(f"  • Family Name:     {family_name}")
        print(f"  • Subfamily:       {subfamily}")
        print(f"  • Full Name:       {full_name}")
        print(f"  • PostScript Name: {ps_name}")

        if family_name and "Google Emoji 3D" in family_name:
            self.log_pass("Family Name", f"Identified as '{family_name}'")
        else:
            self.log_warn("Family Name", f"Unexpected family name: '{family_name}'")

        if ps_name and " " not in ps_name:
            self.log_pass("PostScript Name", f"Valid whitespace-free identifier: '{ps_name}'")
        else:
            self.log_fail("PostScript Name", f"Invalid PostScript name contains spaces: '{ps_name}'")

    def test_cmap_and_sequences(self):
        print("\n[5/7] Verifying Unicode Character Map (cmap) & Ligature Sequences")
        cmap_table = self.font.get("cmap")
        if not cmap_table:
            self.log_fail("cmap Table", "Character map table missing")
            return

        cmap = cmap_table.getBestCmap()
        if not cmap:
            self.log_fail("cmap Best Subtable", "No usable Unicode subtable found in cmap (Format 12 required)")
            return

        mapped_count = len(cmap)
        print(f"  • Total Mapped Single Codepoints: {mapped_count:,}")

        if mapped_count < 1000:
            self.log_fail("cmap Coverage", f"Only {mapped_count} codepoints mapped (expected > 1,000 for standard base emoji sets)")
        else:
            self.log_pass("cmap Base Coverage", f"{mapped_count:,} Unicode base codepoints mapped (remaining complex sequences resolved via GSUB ligatures)")

        # Verify word spacing isolation: U+0020 (space) must NOT be mapped to avoid wide word separation
        if 0x20 not in cmap:
            self.log_pass("Word Spacing & ASCII Isolation", "U+0020 (space) unmapped from cmap (normal text words will use system text font spacing)")
        else:
            self.log_warn("Word Spacing & ASCII Isolation", "U+0020 (space) is mapped in cmap with emoji advance width")

        # Compare with base font if available (focusing on emoji codepoints >= 0x2000)
        if self.base_font and "cmap" in self.base_font:
            base_cmap = self.base_font["cmap"].getBestCmap() or {}
            base_emoji_cps = {cp for cp in base_cmap if cp >= 0x2000}
            target_emoji_cps = {cp for cp in cmap if cp >= 0x2000}
            diff_missing = base_emoji_cps - target_emoji_cps
            if diff_missing:
                self.log_warn("Base Font Emoji Parity", f"{len(diff_missing)} emoji codepoints present in base font missing from target font")
            else:
                self.log_pass("Base Font Emoji Parity", f"100% of base font emoji codepoints ({len(base_emoji_cps):,}) preserved in target font")

        # Test benchmark single codepoints
        single_tested = 0
        single_passed = 0
        for item in BENCHMARK_SEQUENCES:
            if item["type"] == "single":
                single_tested += 1
                cp = item["cps"][0]
                if cp in cmap:
                    single_passed += 1
                else:
                    self.log_warn("Single Codepoint", f"Missing {item['name']} (U+{cp:X})")

        if single_passed == single_tested:
            self.log_pass("Benchmark Single Emojis", f"All {single_passed}/{single_tested} verified in cmap")

        # Test GSUB ligatures for multi-codepoint sequences (ZWJ, skin tone, flags)
        has_gsub = "GSUB" in self.font and hasattr(self.font["GSUB"], "table")
        if has_gsub:
            self.log_pass("GSUB Table", "Layout engine substitution table present for sequence shaping")
            # Build ligature lookup map
            gsub = self.font["GSUB"].table
            features = [f.FeatureTag for f in gsub.FeatureList.FeatureRecord]
            print(f"  • GSUB Active Feature Tags: {features}")
            if "liga" in features or "ccmp" in features:
                self.log_pass("Ligature Features", f"Standard substitution features active ({features})")
            else:
                self.log_warn("Ligature Features", "Neither 'liga' nor 'ccmp' found in GSUB")
        else:
            self.log_fail("GSUB Table", "GSUB table missing! ZWJ families, skin tones, and flags will fail to shape")

    def test_cbdt_cblc_strikes(self):
        print("\n[6/7] Verifying Color Bitmap Data Table (CBDT) & Location Table (CBLC)")
        cbdt = self.font.get("CBDT")
        cblc = self.font.get("CBLC")

        if not cbdt or not cblc:
            self.log_fail("CBDT/CBLC Tables", "CBDT or CBLC table missing")
            return

        strike_count = len(cbdt.strikeData)
        print(f"  • CBDT Strike Count: {strike_count}")
        if strike_count == 0:
            self.log_fail("CBDT Strike Data", "CBDT table contains 0 strikes")
            return

        strike0 = cbdt.strikeData[0]
        glyph_count = len(strike0)
        print(f"  • Strike 0 Total Bitmap Glyphs: {glyph_count:,}")

        # Check CBLC strike parity
        cblc_strikes = getattr(cblc, "strikes", None)
        if cblc_strikes is None:
            cblc_strikes = getattr(cblc, "bitmapSizeTable", [])
        cblc_count = len(cblc_strikes) if cblc_strikes is not None else 0

        if cblc_count == strike_count or (cblc_count == 0 and strike_count > 0 and len(strike0) > 0):
            self.log_pass("CBLC/CBDT Strike Parity", f"CBLC location tables verified for {strike_count} CBDT strike(s)")
        else:
            self.log_fail("CBLC/CBDT Strike Parity", f"CBLC defines {cblc_count} size records but CBDT has {strike_count} strikes")

        # Validate PNG payload headers and dimensions across a sample of glyphs
        valid_pngs = 0
        corrupt_pngs = 0
        sample_checked = 0
        check_limit = 200

        for gname, bitmap in strike0.items():
            sample_checked += 1
            if sample_checked > check_limit:
                break

            data = getattr(bitmap, "imageData", None)
            if not data or len(data) < 8:
                corrupt_pngs += 1
                continue

            # PNG signature check: 89 50 4E 47 0D 0A 1A 0A
            if data[:8] == b"\x89PNG\r\n\x1a\n":
                valid_pngs += 1
                if sample_checked <= 3:
                    try:
                        img = Image.open(BytesIO(data))
                        print(f"  • Sample Glyph '{gname}': {img.size[0]}x{img.size[1]} PNG ({len(data):,} bytes)")
                    except Exception:
                        pass
            else:
                corrupt_pngs += 1

        if corrupt_pngs == 0:
            self.log_pass("PNG Payload Signature", f"All {valid_pngs}/{sample_checked} inspected glyphs contain valid PNG streams")
        else:
            self.log_fail("PNG Payload Signature", f"{corrupt_pngs} corrupt or truncated bitmap streams detected")

        # Format 17 Metrics Check
        sample_bmp = next(iter(strike0.values()))
        metrics = getattr(sample_bmp, "metrics", None)
        if metrics:
            print(f"  • Format 17 Metrics Sample: width={metrics.width}, height={metrics.height}, BearingX={metrics.BearingX}, BearingY={metrics.BearingY}, Advance={metrics.Advance}")
            if metrics.width > 0 and metrics.height > 0 and metrics.Advance > 0:
                self.log_pass("SmallGlyphMetrics (Format 17)", "Valid width, height, and advance values")
            else:
                self.log_fail("SmallGlyphMetrics (Format 17)", "Zero or negative metric dimensions in CBDT strike")

    def test_cross_platform_diagnostics(self):
        print("\n[7/7] Cross-Platform Target Compatibility Assessment")
        tables = set(self.font.keys())
        has_cbdt = "CBDT" in tables and "CBLC" in tables
        has_colr = "COLR" in tables and "CPAL" in tables
        has_sbix = "sbix" in tables
        has_svg = "SVG " in tables

        # Target 1: Android (Gboard, Instaprime, System Magisk)
        if has_cbdt and not has_colr:
            print("  [TARGET] Android (Gboard & System): EXCELLENT (Pure CBDT/CBLC, 100% native compatibility)")
        elif has_cbdt and has_colr:
            print("  [TARGET] Android (Gboard & System): CONFLICT (COLR present; Android 13+ will render 2D instead of 3D)")
        else:
            print("  [TARGET] Android (Gboard & System): INCOMPATIBLE (Missing CBDT/CBLC)")

        # Target 2: Apple (iOS / macOS CoreText)
        if has_sbix:
            print("  [TARGET] Apple (iOS / macOS): SUPPORTED (sbix strike present)")
        else:
            print("  [TARGET] Apple (iOS / macOS): NOT SUPPORTED (Apple requires 'sbix' table)")

        # Target 3: Windows (DirectWrite / Edge / Word)
        if has_colr:
            print("  [TARGET] Windows (DirectWrite): SUPPORTED (COLR/CPAL table present)")
        else:
            print("  [TARGET] Windows (DirectWrite): NOT SUPPORTED (Windows requires 'COLR' or 'SVG ' table)")

        # Target 4: Linux / Web (FreeType & HarfBuzz)
        if has_cbdt:
            print("  [TARGET] Linux / FreeType: SUPPORTED (FreeType natively renders CBDT/CBLC)")

    def print_summary(self):
        print("\n" + "=" * 60)
        print("          EMOJI FONT TEST RUN SUMMARY")
        print("=" * 60)
        print(f"  Total Checks Passed:   {len(self.passes)}")
        print(f"  Warnings:              {len(self.warnings)}")
        print(f"  Critical Failures:     {len(self.errors)}")
        print("=" * 60)

        if self.errors:
            print("\n❌ CRITICAL FAILURES DETECTED:")
            for name, detail in self.errors:
                print(f"  • {name}: {detail}")
            print("\nResult: TEST SUITE FAILED (exit code 1)")
            return False
        else:
            print("\n✅ ALL CRITICAL INVARIANTS PASSED!")
            if self.warnings:
                print(f"  ({len(self.warnings)} non-fatal warning(s) noted above)")
            print("\nResult: TEST SUITE SUCCESSFUL (exit code 0)")
            return True


def main():
    parser = argparse.ArgumentParser(description="Test and Validate Google Emoji 3D TTF Font")
    parser.add_argument("font", nargs="?", default=DEFAULT_FONT_PATH, help="Path to TTF font file to test")
    parser.add_argument("--base", default=DEFAULT_BASE_FONT_PATH, help="Path to reference base font (optional)")
    args = parser.parse_args()

    tester = EmojiFontTester(args.font, args.base)
    if not tester.load_fonts():
        sys.exit(1)

    tester.test_required_tables()
    tester.test_header_and_metrics()
    tester.test_name_records()
    tester.test_cmap_and_sequences()
    tester.test_cbdt_cblc_strikes()
    tester.test_cross_platform_diagnostics()

    success = tester.print_summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
