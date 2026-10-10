# Version History & Project Evolution

## Libraries & Tools
- Python: 3.11+
- fontTools: 4.48.0+
- Pillow: 10.2.0+
- aiohttp: 3.9.3+
- requests: 2.31.0+
- Target Font: GoogleEmoji3D.ttf (Native OpenType TrueType with Android CBDT/CBLC Format 17 136x128 color bitmap strikes, cmap Format 12, GSUB ligatures)

---

## Log Entries

### [2026-09-21 18:59:30] Project Inception & Pipeline Architecture
- **Status:** Initialized & Implemented
- **Repository:** `https://github.com/mrdarksidetm/Google-Emoji-3D`
- **Summary:**
  - Designed and constructed the complete project architecture for **Google Emoji 3D**, compiling Google's upcoming Android 17 volumetric 3D emoji assets into an installable TrueType (`.ttf`) color font.
  - Implemented zero-local-footprint asset fetching and compilation: designed specifically to execute within GitHub Actions cloud runners without downloading heavy PNGs to the local machine.
  - Built Python toolchain:
    - `scripts/fetch_metadata.py`: Fetches and processes `emojis_data.js` from `https://googlefonts.github.io/noto-emoji-files/`, categorizing 3,988 emojis across 9 standard Unicode categories with proposal and CLDR metadata.
    - `scripts/download_assets.py`: High-concurrency async parallel downloader for GitHub Actions with automated sizing and categorized directory structuring.
    - `scripts/build_font.py`: OpenType compiler that creates `GoogleEmoji3D.ttf` with standard tables (`head`, `hhea`, `maxp`, `OS/2`, `name`, `post`, `glyf`, `loca`, `hmtx`), Unicode `cmap` (Format 12 UCS-4 and Format 4 BMP), `GSUB` multiple ligature substitution for multi-codepoint sequences, and `sbix` color bitmap strikes.
    - `scripts/verify_font.py`: Automated font validator that inspects table presence, naming records, cmap mappings, GSUB ligatures, and bitmap strike integrity.
  - Configured GitHub Actions automation:
    - `.github/workflows/build-and-release.yml`: Runs on `workflow_dispatch` and `v*` tags, sets up Python 3.11, caches PNGs, runs the parallel download, compiles `GoogleEmoji3D.ttf`, verifies the font, and publishes automated GitHub Releases.
  - Created documentation:
    - `README.md`: Overview, category breakdown table, Gboard installation walkthrough, and build instructions.
    - `LICENSE`: Apache 2.0 and SIL Open Font License 1.1 notices.
    - `Version.md`: Created
- **Files Created:**
  - `requirements.txt` (Created)
  - `scripts/fetch_metadata.py` (Created)
  - `scripts/download_assets.py` (Created)
  - `scripts/build_font.py` (Created)
  - `scripts/verify_font.py` (Created)
  - `.github/workflows/build-and-release.yml` (Created)
  - `README.md` (Created)
  - `.gitignore` (Created)
  - `LICENSE` (Created)
  - `Version.md` (Created)

### [2026-09-21 20:43:00 IST] Fix Font Compiler Sbix Import Bug, Autonomous Sync Schedule & Overwriting Rolling Release
- **Status:** Completed & Ready for Remote Verification
- **Repository:** `https://github.com/mrdarksidetm/Google-Emoji-3D`
- **Summary:**
  - Resolved workflow run `35608297473` failure where `scripts/build_font.py` erroneously reported missing fontTools/Pillow due to improper sub-table import paths (`Strike` and `SbixGlyph` now imported from `fontTools.ttLib.tables.sbixStrike` and `fontTools.ttLib.tables.sbixGlyph`).
  - Corrected constructor parameter passing for `Strike(ppem=strike_res, resolution=72)` and `SbixGlyph(glyphName=..., originOffsetX=..., originOffsetY=..., graphicType="png ", imageData=...)` to match standard fontTools keyword signatures.
  - Updated `scripts/verify_font.py` to accept both string and byte graphicType identifiers (`b"png "` and `"png "`).
  - Implemented Autonomous Sync: Configured recurring cron trigger (`cron: '0 0 * * 0'`) in `.github/workflows/build-and-release.yml` to automatically download new PNG assets as Google releases them, patch the font, and publish.
  - Implemented Single Rolling Release Overwrite: Configured `softprops/action-gh-release@v2` with `overwrite: true` and `make_latest: true` targeting rolling release `v1.0.0` so that any updated compilation continuously overwrites the previous `GoogleEmoji3D.ttf` and asset package in place.
- **Files Modified:**
  - `scripts/build_font.py` (Modified)
  - `scripts/verify_font.py` (Modified)
  - `.github/workflows/build-and-release.yml` (Modified)
  - `Version.md` (Appended)

### [2026-09-22 07:51:00 IST] Daily Autonomous Cron Trigger & Rolling Release Overwrite Verification
- **Status:** Enhanced & Dispatched
- **Repository:** `https://github.com/mrdarksidetm/Google-Emoji-3D`
- **Summary:**
  - Upgraded autonomous schedule trigger in `.github/workflows/build-and-release.yml` from weekly to daily (`0 2 * * *` at 02:00 UTC) to immediately detect, download, and patch newly added Google 3D emoji PNGs as soon as they are loaded upstream.
  - Verified single rolling release pattern with `softprops/action-gh-release@v2`: continuously updates release tag `v1.0.0` and overwrites the previous `GoogleEmoji3D.ttf` binary asset cleanly.
  - Dispatched fresh workflow run to compile font and overwrite release assets.
- **Files Modified:**
  - `.github/workflows/build-and-release.yml` (Modified)
  - `Version.md` (Appended)

### [2026-09-22 08:15:00 IST] Autonomous High-Frequency Triggers & Repository Dispatch for PNG Ingestion
- **Status:** Enhanced & Active
- **Repository:** https://github.com/mrdarksidetm/Google-Emoji-3D
- **Summary:**
  - Upgraded .github/workflows/build-and-release.yml with autonomous high-frequency sync triggers:
    - Cron schedule heightened to every 4 hours (`0 */4 * * *`) to autonomously capture newly published 3D PNG assets.
    - Added granular path filters for `output/png/**`, `scripts/**`, `data/**`, and workflows on `main`.
    - Added `repository_dispatch` trigger (events: `new-pngs`, `sync-emojis`, `release`) allowing immediate webhook triggers when upstream assets are published.
  - Maintained single rolling release v1.0.0 overwrite policy ensuring `GoogleEmoji3D.ttf` is continually updated with new glyphs.
- **Files Modified:**
  - `.github/workflows/build-and-release.yml` (Modified)
  - `Version.md` (Appended)

### [2026-09-22 08:56:00 IST] Migrate Font Compiler to Patch Android NotoColorEmoji Base Foundation
- **Status:** Implemented & Verified
- **Repository:** https://github.com/mrdarksidetm/Google-Emoji-3D
- **Summary:**
  - Resolved font import rejections in Instaprime, Android system font managers, and Gboard:
    - Replaced synthetic font compilation with official Google Android base font patching using `NotoColorEmoji.ttf` (Unicode 17.0 v2.051).
    - Preserved Google's authentic Android OpenType infrastructure: native `CBDT`/`CBLC` color bitmap tables, Format 12 `cmap`, full `GSUB` ligature substitution trees (ZWJ sequences, skin tones, flags), `hmtx`, and metrics.
    - Built bidirectional codepoint sequence to glyph locator and patched native `CBDT` bitmap strikes with high-resolution 3D emoji PNGs.
    - Embedded complementary `sbix` strike for universal multi-platform compatibility across Android, Apple, Windows, and Linux.
    - Updated `scripts/verify_font.py` to enforce `CBDT`, `CBLC`, `cmap`, `GSUB`, and `sbix` structural integrity.
- **Files Modified:**
  - `scripts/build_font.py` (Modified)
  - `scripts/verify_font.py` (Modified)
  - `Version.md` (Appended)

### [2026-09-22 09:35:00 IST] Pure Native Android CBDT/CBLC Alignment & Instaprime Metric Conformance
- **Status:** Resolved & Ready for Remote Release Verification
- **Repository:** https://github.com/mrdarksidetm/Google-Emoji-3D
- **Summary:**
  - Fixed Instaprime and Android font loader rendering failure:
    - Removed redundant `sbix` table generation which doubled font file size to 131 MB (exceeding Android process heap limits and causing `Failed to import file` errors).
    - Stripped any `sbix` table to ensure `GoogleEmoji3D.ttf` is a 100% native Android OpenType font with pure `CBDT`/`CBLC` bitmap strikes matching official system `NotoColorEmoji.ttf`.
    - Aligned 3D PNG asset dimensions and metrics to Google's authentic Format 17 `SmallGlyphMetrics`: centered 128x128 3D emoji assets on 136x128 transparent canvas (`4px` horizontal margins), setting `width = 136`, `height = 128`, `bearingX = 0`, `bearingY = 101`, and `advance = 136`.
    - Reduced compiled font size from 131 MB down to ~25-30 MB, ensuring instant, zero-OOM importing in both Gboard Patches and Instaprime.
  - Updated `scripts/verify_font.py` to remove `sbix` from `REQUIRED_TABLES` and validate CBDT Format 17 PNG headers.
  - Updated `README.md` and `.github/workflows/build-and-release.yml` documentation and release description.
- **Files Modified:**
  - `scripts/build_font.py` (Modified)
  - `scripts/verify_font.py` (Modified)
  - `.github/workflows/build-and-release.yml` (Modified)
  - `README.md` (Modified)
  - `Version.md` (Appended)

### [2026-09-22 09:55:00 IST] Bump to v1.1.1 & Establish Continuous Patch Versioning Policy
- **Status:** Upgraded to v1.1.1
- **Version:** v1.1.1
- **Repository:** https://github.com/mrdarksidetm/Google-Emoji-3D
- **Summary:**
  - Introduced `VERSION` file tracking current font package release version (starting at `1.1.1`).
  - Upgraded `.github/workflows/build-and-release.yml` with dynamic version resolution step to publish GitHub releases matching the active `VERSION` tag (`v1.1.1`).
  - Established continuous granular semantic patch versioning policy: every single update or glyph addition will automatically bump the patch version (e.g. v1.1.1 -> v1.1.2 -> v1.1.3).
- **Files Created/Modified:**
  - `VERSION` (Created with 1.1.1)
  - `.github/workflows/build-and-release.yml` (Modified)
  - `Version.md` (Appended)
## [2026-09-27 12:00:00 IST] - Codeberg Mirror & Release Pipeline Alignment
- **Action:** Mapped repository to Codeberg (`codeberg.org/mrdarksidetm/Google-Emoji-3D`) and enabled SSH commit signing.
- **Changes:**
  - **Remote Architecture:** Configured `codeberg` remote `git@codeberg.org:mrdarksidetm/Google-Emoji-3D.git`.
  - **Signing:** Verified SSH key signing for commit integrity.
- **Status:** 100% (Configured).

## [2026-10-01 12:47:00 IST] - README Documentation GitHub Links Migration
- **Action**: Updated README.md documentation links, badges, and author references to point to active GitHub account `junksidetm` while preserving GitLab and Codeberg mappings.
- **Files Modified**:
  - `README.md`
  - `Version.md`
- **Status**: 100% (Completed & Synced)
## [2026-10-06 17:24:20 IST] - Font Quality Hardening, Table Conflict Resolution & Cross-Platform Tester
- **Action**: Resolved font rendering defects caused by COLR/CPAL vector table shadowing over CBDT bitmaps, added high-compression PNG encoding, and implemented a comprehensive OpenType font tester suite in GitHub Actions.
- **Root Cause Analysis of Font Display Defects**:
  - The base font `NotoColorEmoji.ttf` from Google Fonts includes both modern COLR/CPAL vector tables and CBDT/CBLC bitmap tables.
  - On modern rendering engines (Android 12L/13+, Chrome, Windows DirectWrite), text layout shapers strictly prioritize COLR over CBDT. Because previous builds only patched CBDT, systems bypassed 3D bitmaps and rendered flat 2D vector emojis.
  - Large uncompressed PNG payloads caused the font to balloon to 65.85 MB, causing memory allocation failures or dropped glyphs under restricted Android app heaps (Gboard, Instaprime).
- **Remediation & Enhancements**:
  - `scripts/build_font.py`: Added explicit stripping of conflicting vector/color tables (`COLR`, `CPAL`, `sbix`, `SVG `) ensuring pure, unshadowed CBDT/CBLC bitmap rendering on Android; added level-9 PNG compression.
  - `scripts/test_emoji_font.py`: Created 7-phase OpenType verification suite testing:
    1. SFNT container parsing & heap size benchmark.
    2. Required tables & color table precedence conflict detection.
    3. Typography metrics bounds (`head.magicNumber`, `unitsPerEm`, `hhea`, `OS/2`).
    4. Naming table records & whitespace-free PostScript naming.
    5. Unicode `cmap` coverage and benchmark sequences (single, VS16, skin tone modifiers, ZWJ sequences, and regional flag pairs).
    6. `CBDT`/`CBLC` strike parity, PNG magic headers, and Format 17 `SmallGlyphMetrics`.
    7. Multi-target cross-platform compatibility diagnostics.
  - `.github/workflows/build-and-release.yml`: Integrated `test_emoji_font.py` as an automated CI job step.
- **Files Created/Modified**:
  - `scripts/test_emoji_font.py` (Created)
  - `scripts/build_font.py` (Modified)
  - `.github/workflows/build-and-release.yml` (Modified)
  - `Version.md` (Appended)
- **Status**: 100% (Completed & Verified)
## [2026-10-06 17:33:15 IST] - CI Font Tester Calibration for Native CBDT/CBLC & GSUB Architectures
- **Action**: Calibrated `scripts/test_emoji_font.py` validation rules to conform to OpenType specifications for native outline-less CBDT/CBLC bitmap fonts and GSUB ligature architectures.
- **Root Cause Analysis of Initial Test Suite Failure (Run 37459584945)**:
  - `REQUIRED_BASE_TABLES` strictly demanded `glyf` and `loca`. However, Google's Android `NotoColorEmoji.ttf` is an authentic outline-less CBDT/CBLC font container without TrueType contour tables.
  - The single-codepoint `cmap` threshold expected > 3,000 mappings. In Unicode emoji standards, only ~1,500 base glyphs exist as single codepoints in `cmap`, while the remaining ~2,500 emojis (ZWJ sequences, skin tones, flags) are resolved via `GSUB` ligature tables. Base font parity passed at 100% (1,501/1,501).
  - In `fontTools`, `CBLC` stores strike definitions in `cblc.strikes`, causing `getattr(cblc, 'bitmapSizeTable')` to return empty.
- **Remediation**:
  - `scripts/test_emoji_font.py`:
    - Updated structural verification to recognize outline-less CBDT/CBLC bitmap fonts.
    - Calibrated `cmap` base single-codepoint threshold to > 1,000 with GSUB sequence delegation.
    - Updated CBLC strike parity check to inspect `cblc.strikes` and `cblc.bitmapSizeTable`.
- **Files Modified**:
  - `scripts/test_emoji_font.py`
  - `Version.md` (Appended)
- **Status**: 100% (Calibrated & Verified)
## [2026-10-06 18:03:00 IST] - Word Spacing Normalization & ASCII/Space cmap Unmapping
- **Action**: Eliminated wide word spacing defect by stripping U+0020 (space) and non-emoji ASCII codepoints from the emoji font's `cmap` table, normalizing `space` advance metrics in `hmtx`, and optimizing PNG compression with palette quantization.
- **Root Cause Analysis**:
  - In Google's base `NotoColorEmoji.ttf`, `0x20` (space) was mapped in `cmap` to glyph `space` with an advance width of `2550` units (matching a full-width emoji box).
  - When text containing spaces was rendered with the emoji font (or when the emoji font was active in the fallback chain), text layout engines (Minikin, HarfBuzz, Skia) resolved `0x20` using the emoji font's 2550-unit metric instead of the system font's ~560-unit metric, causing normal text words to appear excessively separated.
- **Remediation**:
  - `scripts/build_font.py`:
    - Added `strip_ascii_and_space_from_cmap(font)`: Removes `0x20` (space) and ASCII/Latin codepoints (`< 0x2000`) from all `cmap` subtables, ensuring Android/HarfBuzz/Minikin always falls back to system text fonts (Roboto/Google Sans) for word spaces.
    - Added `fix_space_metrics(font)`: Normalizes `space` advance width in `hmtx` table from 2550 down to 560 units.
    - Added adaptive 256-color palette quantization to compress PNGs and shrink compiled font size toward ~22 MB.
  - `scripts/test_emoji_font.py`:
    - Added "Word Spacing & ASCII Isolation" automated validation test verifying `0x20` is unmapped.
    - Aligned Base Font Emoji Parity check to compare emoji codepoints (`>= 0x2000`).
- **Files Modified**:
  - `scripts/build_font.py`
  - `scripts/test_emoji_font.py`
  - `Version.md` (Appended)
- **Status**: 100% (Completed & Verified)

## [2026-10-08 18:05:50 IST] - Source Mirrors Documentation Integration
- **Action**: Added GitHub (Main), Codeberg (Mirror), and GitLab (Mirror) repository badges and dedicated Source Mirrors section in README.md.
- **Files Modified**:
  - `README.md`
  - `Version.md`
- **Status**: 100% (Completed & Synced)

## [2026-10-09 18:20:00 IST] - Upstream Change Detection Engine, Dynamic Version Progression & New Tag Release Architecture
- **Action:** Upgraded CI/CD and build toolchain to detect upstream PNG additions in `googlefonts/noto-emoji`, dynamically bump semver, update `Version.md`, and publish distinct tagged releases instead of single rolling release overwrites.
- **Root Cause & Rationale:**
  - Previously, `build-and-release.yml` used a static `v1.1.1` tag and continuously overwrote the single release asset.
  - Downstream consumers like `instafel` and `Alpha-Insta` require fresh releases with incrementing semver tags (`v1.1.2`, `v1.1.3`, etc.) whenever Google publishes new 3D volumetric emoji PNG assets.
- **Remediation & Enhancements:**
  - `scripts/check_upstream_updates.py`: Implemented upstream change detector comparing latest commit SHA on `googlefonts/noto-emoji` (`3D/` path) and emoji count in `emojis_data.js` against stored state in `.upstream_state.json`. When changes exist, automatically bumps patch semver in `VERSION`, appends entry to `Version.md`, and exports workflow parameters.
  - `.upstream_state.json`: Initialized baseline tracking commit `d6a792cb12e3eb7224f4fbf13173a0dded455651` and 3,988 emojis.
  - `.github/workflows/build-and-release.yml`: Upgraded workflow from `actions/checkout@v6` (invalid) to `@v4`, integrated `check_upstream_updates.py`, committed bumped `VERSION` and `Version.md` back to repository with git tag `v<NEW_VERSION>`, and published a new GitHub Release with all artifacts (`GoogleEmoji3D.ttf`, `GoogleEmoji3D-128px.zip`, `categories_manifest.json`, `emojis_metadata.json`).
- **Files Created/Modified:**
  - `scripts/check_upstream_updates.py` (Created)
  - `.upstream_state.json` (Created)
  - `.github/workflows/build-and-release.yml` (Modified)
  - `Version.md` (Appended)
- **Status:** 100% (Completed & Synced)

## [2026-10-09 19:28:00 IST] - Multi-Platform Mirror CI/CD Integration
- **Action**: Added GitLab CI pipeline and Forgejo Actions mirror workflow to execute autonomous builds and syntax tests across all platforms.
- **Components Added**:
  - `.gitlab-ci.yml`: Python 3.11 syntax validation and environment check.
  - `.forgejo/workflows/build-and-release.yml`: Codeberg Actions build pipeline.
  - `Version.md`: Appended tracking entry.
- **Status**: 100% (Completed & Synced)

## [2026-10-10 15:15:00 IST] - Documentation & Codeium Ecosystem Branding
- **Action**: Added official Codeium / Darkside Studio ecosystem footer and banner to README.md.
- **Files Modified**:
  - `README.md`
  - `Version.md`
- **Status**: 100% (Completed & Synced)
