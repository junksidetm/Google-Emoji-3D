# Google Emoji 3D 🎨

<p align="center">
  <b>TrueType (.ttf) Color Emoji Font compiled from Google's official 3D Noto Emoji assets (Android 17 Preview style)</b>
</p>

<p align="center">
  <a href="https://github.com/junksidetm/Google-Emoji-3D/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/mrdarksidetm/Google-Emoji-3D?display_name=tag&label=Release&style=for-the-badge"></a>
  <a href="https://github.com/junksidetm/Google-Emoji-3D/actions/workflows/build-and-release.yml"><img alt="Build status" src="https://img.shields.io/github/actions/workflow/status/mrdarksidetm/Google-Emoji-3D/build-and-release.yml?style=for-the-badge&label=Build"></a>
  <a href="https://github.com/junksidetm/Gboard-patches"><img alt="Gboard Patches Compatible" src="https://img.shields.io/badge/Gboard%20Patches-Compatible-4285F4?style=for-the-badge"></a>
</p>

---

## 🌟 Overview

**Google Emoji 3D** transforms Google's official volumetric 3D emoji designs (introduced for upcoming Android 17 releases) into an installable, system-wide TrueType font (`.ttf`).

Just as Apple (iOS), Samsung, WhatsApp, and Facebook apply custom visual stylings over the standard Unicode character repertoire, Google Emoji 3D renders standard Unicode emoji characters using Google's volumetric 3D artwork.

All assets are fetched, categorized, and compiled entirely in **GitHub Actions cloud runners**, meaning **zero disk bloat or heavy RAM usage on local machines**.

---

## ✨ Key Features

- **3,900+ Volumetric 3D Emojis:** Covers all standard Unicode emojis, ZWJ sequences, skin tones, gender variants, flags, and keycaps.
- **Categorized Taxonomy:** Structured following the official Google Fonts Emoji hierarchy ([googlefonts.github.io/noto-emoji-files](https://googlefonts.github.io/noto-emoji-files/)):
  - Smileys & Emotion
  - People & Body
  - Animals & Nature
  - Food & Drink
  - Activity
  - Travel & Places
  - Objects
  - Symbols
  - Flags
- **Native Android & OpenType Compatibility:**
  - Native Android `CBDT`/`CBLC` Color Bitmap Data and Location tables preserving official `NotoColorEmoji` metrics.
  - Unicode `cmap` Format 12 (32-bit UCS-4) mapping all standard emoji codepoints.
  - OpenType `GSUB` Ligature Substitution (LookupType 4) for multi-codepoint ZWJ sequences.
- **Rootless Gboard & Instaprime Integration:** Works seamlessly with Instaprime and the **Custom Emoji Font (.ttf)** feature in [mrdarksidetm/Gboard-patches](https://github.com/junksidetm/Gboard-patches) without requiring root, Magisk, or system partition modifications!

---

## 📂 Category Breakdown

All emojis in `Google Emoji 3D` are indexed with their original Unicode proposal metadata, CLDR names, and categories:

| Category | Emoji Count | Description | Sample Glyphs |
| :--- | :---: | :--- | :--- |
| **Smileys & Emotion** | 144 | Classic yellow faces, expressions, hearts, and emotions | 😀 😃 🥰 😂 🥳 🥺 💖 |
| **People & Body** | 2,427 | Gestures, professions, families, fantasy, and skin tone variants | 👍 🫶 👩‍💻 🏃‍♂️ 🧑‍🔬 🤹 |
| **Animals & Nature** | 160 | Mammals, birds, reptiles, sea creatures, plants, and weather | 🐶 🐱 🦁 🌸 🌲 🌊 ☀️ |
| **Food & Drink** | 131 | Fruits, vegetables, prepared meals, snacks, and beverages | 🍎 🍕 🍔 🍣 🍩 ☕ 🧃 |
| **Activity** | 85 | Sports, fitness, arts, games, and entertainment | ⚽ 🏀 🎾 🎮 🎨 🛹 🎸 |
| **Travel & Places** | 219 | Vehicles, architecture, maps, nature landscapes, and transport | 🚗 ✈️ 🚀 🏖️ 🗽 🏔️ 🚂 |
| **Objects** | 267 | Tools, electronic devices, books, clothing, and office supplies | 📱 💻 📷 💡 🔑 📦 🕶️ |
| **Symbols** | 274 | Geometric shapes, zodiac, arrows, multimedia controls, and badges | 💖 ⚡ 🔔 🛑 ➡️ 🔲 💯 |
| **Flags** | 281 | Regional indicators, national flags, and sub-division banners | 🇺🇸 🇮🇳 🇯🇵 🇬🇧 🇩🇪 🇫🇷 🏁 |

---

## 🚀 How to Use in Gboard

You can load `GoogleEmoji3D.ttf` directly into Gboard on any Android device using our custom Morphe patch:

1. **Download Font:** Grab `GoogleEmoji3D.ttf` from the [Latest Releases](https://github.com/junksidetm/Google-Emoji-3D/releases/latest).
2. **Open Gboard Settings:** Navigate to **Gboard Patches** > **Custom Emoji Font (.ttf)**.
3. **Select Font:**
   - Tap **Enable Custom Emoji Font**.
   - Tap **Select .ttf Font File** and pick `GoogleEmoji3D.ttf` from your device storage.
4. **Live Preview:** Check the in-app preview card to see the 3D glyphs immediately rendered.
5. **Type in 3D:** Open any text field — your Gboard keyboard now displays the 3D emoji set!

---

## ⚙️ Building via GitHub Actions

Because high-resolution PNGs take substantial bandwidth and memory, building is automated via GitHub Actions cloud runners:

1. Fork or push this repository to GitHub.
2. Go to **Actions** > **Build and Release Google Emoji 3D TTF**.
3. Click **Run workflow**:
   - Choose your desired resolution (`128px`, `160px`, etc.).
   - Set concurrency (`50`).
   - Click **Run workflow**.
4. The workflow will:
   - Fetch metadata from `googlefonts.github.io/noto-emoji-files`.
   - Download the 3D PNG assets in parallel across 50 concurrent streams.
   - Build `GoogleEmoji3D.ttf` with OpenType color tables.
   - Run verification tests.
   - Publish a new GitHub Release with the compiled font.

---

## 🛠️ Repository Architecture

```
Google-Emoji-3D/
├── .github/
│   └── workflows/
│       └── build-and-release.yml    # Automated cloud build & release workflow
├── data/
│   ├── categories_manifest.json     # Categorized taxonomy & subgroup index
│   └── emojis_metadata.json         # Full Unicode & proposal metadata catalog
├── scripts/
│   ├── fetch_metadata.py            # Extracts metadata from Google Fonts Emoji
│   ├── download_assets.py           # Parallel cloud asset fetcher
│   ├── build_font.py                # OpenType TTF color font compiler (sbix/cmap/GSUB)
│   └── verify_font.py               # Font validation and table health checker
├── requirements.txt                 # Python dependencies (fonttools, pillow, aiohttp)
├── LICENSE                          # SIL Open Font License 1.1 / Apache 2.0
└── README.md                        # Documentation & setup guide
```

---

## 📜 Credits & Attribution

- **Project Creator & Maintainer:** [@junksidetm](https://github.com/junksidetm) — Font compilation engine, GitHub Actions build system, categorization, and Gboard integration.
- **Original 3D Artwork & Assets:** [Google LLC](https://github.com/googlefonts/noto-emoji) — Designed by the Google Noto Emoji team.
- **Data Source:** [Google Fonts Noto Emoji Files](https://googlefonts.github.io/noto-emoji-files/).

---

## ⚖️ License

The font code and compilation scripts are licensed under the **Apache License, Version 2.0**.
The underlying Google 3D Emoji designs and assets are licensed by Google under the **SIL Open Font License, Version 1.1**.
