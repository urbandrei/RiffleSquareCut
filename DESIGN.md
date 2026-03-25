# Design Decisions

This section captures all design decisions made for the Riffle Square Cut website, organized by category. These decisions were made through a structured questionnaire and serve as the definitive design brief for implementation.

---

## 1. Brand Identity

**Q: What does the Hidden Marks logo look like?**
A: It is a symbol/icon -- either 3 squares side by side or a cube-like profile (see `RSC_logo_black.png`).

**Q: What colors appear in the existing logo and card art?**
A: Black, white, red, and blue.

**Q: What is the art style of the card illustrations?**
A: The backs look like luxury playing cards; the fronts are minimal, geometric, and functional.

**Q: Does Hidden Marks have any lore or backstory?**
A: Yes -- a world of assassins trying to kill each other in the Hidden Mark Society.

**Q: What's the relationship between "Riffle Square Cut" and "Hidden Marks"?**
A: Riffle Square Cut is the company/brand. Hidden Marks is the product (card game).

---

## 2. Color Palette

**Primary palette:** Black, white, Red `#EF3B38`, Blue `#4EC8ED`.

These are the exact colors from the card designs. No additional accent colors.

---

## 3. Typography

**Q: Do you have existing font preferences or should we choose from scratch?**
A: Choose from scratch.

**Q: Use monospace fonts (JetBrains Mono, IBM Plex Mono) for prices, data, and code-like elements?**
A: Yes, love it.

**Q: ALL CAPS or mixed case for headlines and hero text?**
A: ALL CAPS everywhere.

---

## 4. Brand Voice & Positioning

**Q: What is the brand voice / tone?**
A: Bold & confrontational.

**Q: Who is the primary target audience?**
A: 18-30 gamers / hobbyists.

**Q: How should the website position Hidden Marks in terms of price/prestige?**
A: Underground / exclusive.

**Q: What emotion should a first-time visitor feel within 3 seconds?**
A: Excited / energized.

**Q: Any anti-references -- things you DON'T want the site to look like?**
A: No childish/cartoony. No corporate/clean.

---

## 5. Visual Style

**Q: How much graffiti / street art texture?**
A: Subtle accents only.

**Q: How intense should glitch/distortion effects be?**
A: Moderate -- on interactions only.

**Q: How do you feel about the industrial aesthetic layer (metal panels, rivets, warning stripes)?**
A: Going for industrial labels, warnings, stripes, instructions, usage details -- industrial *labels* and aesthetics, not infrastructure.

**Q: How much animation/motion overall?**
A: Maximum juice.

**Q: Should the site have sound effects?**
A: No sound at all.

**Q: Dark mode only, or offer a light mode toggle?**
A: Dark only, no toggle.

---

## 6. Layout & Structure

**Q: What's the vibe for the homepage hero section?**
A: Floating cards and bold typography. Majority of the site should feel flat, with a parallax background and certain elements popping off in 3D space.

**Q: For the parallax background -- what kind of imagery?**
A: Abstract/generative, plus city backgrounds -- skyline, alleyways, the street.

**Q: For the city/urban backgrounds -- illustrated or photographic?**
A: Silhouette / minimal.

**Q: How should the navigation/header feel?**
A: HUD-style overlay.

**Q: What should CTA buttons look like?**
A: Industrial label style.

**Q: For the footer?**
A: Themed terminal / status bar.

**Q: Should the cube logo animate on the site?**
A: Yes, animated on load.

---

## 7. Interactions

**Q: Should hover states feel magnetic, spring-loaded, or smooth?**
A: Mix: magnetic + spring.

**Q: Should the site use scroll-triggered section transitions?**
A: Yes, rich scroll animations.

**Q: What should loading states look like between page transitions?**
A: Glitch transition mixed with skeleton screen.

**Q: Should mobile have the same level of animation/juice as desktop?**
A: Same experience.

---

## 8. Page-Specific Decisions

**Hero:** Floating cards + bold typography with flat layout, parallax background, and selective 3D pop-outs.

**Card Gallery:** Not all cards shown -- specific curated interactive views (one of each color, the box, cards fanned out, etc.).

**3D Card Viewer:** Full 3D rotation on product page.

**Product SKUs:** Single SKU now, expand later.

**Cart & Checkout:** Themed cart, clean checkout (switch to trustworthy look for payment).

**Blog:** Full cyberpunk aesthetic.

**Tutorial:** Full interactive simulation with virtual cards.

**Map (Retail Stores):** Dark-themed custom map.

**Chat Widget:** Custom cyberpunk widget (live chat + AI chatbot + offline messaging).

**Giveaway Page:** Countdown + dramatic reveal.

**Error States (404, empty cart, etc.):** Themed but clear.

**Forms & Sign-In:** Themed frame, clean inputs. Themed but standard UX for sign-in.

**Employee Dashboard:** Completely separate from the customer-facing site.

---

## 9. Features

**Micrographics:** All in -- core feature. Tiny hidden text with game lore, secret codes, discount codes discoverable by careful users.

**Discovery & Secrets:** Subtle hints in micrographics; discovery should feel mostly organic.

**Referral System:** Build infrastructure but hide for now -- for specific brand advocates later.

**Pack Opening Ceremony:** Cool idea, save for later.

**Promo Codes:** Fully themed (e.g., `SHADOW-OPS-20`, `DARKMARKET`).

**Product Reviews:** All types (text, photo, video, ratings).

**Print Materials:** Yes, but site design leads -- print follows the site.

**Social Media:** Multiple platforms, already established.

---

---

# Riffle Square Cut -- Design Research

This document compiles deep research across 12 design topics and brands that inform the visual direction of the Riffle Square Cut website for Hidden Marks. Each section covers specific techniques, color palettes, typography, and implementation guidance relevant to building a dark, cyberpunk-themed, interactive e-commerce experience.

---

## Table of Contents

1. [Micrographics](#1-micrographics)
2. [Video Game Juice](#2-video-game-juice)
3. [Industrial Design Aesthetic](#3-industrial-design-aesthetic)
4. [Cards Against Humanity](#4-cards-against-humanity)
5. [Exploding Kittens](#5-exploding-kittens)
6. [Stonemaier Games](#6-stonemaier-games)
7. [Cyberpunk / Dystopian Design](#7-cyberpunk--dystopian-design)
8. [Graffiti as a Design Element](#8-graffiti-as-a-design-element)
9. [E-Commerce Best Practices](#9-e-commerce-best-practices)
10. [Marathon (Bungie)](#10-marathon-bungie)
11. [MORK BORG](#11-mork-borg)
12. [Cyberpunk 2077](#12-cyberpunk-2077)
13. [Synthesis: Applying It All to Riffle Square Cut](#13-synthesis-applying-it-all-to-riffle-square-cut)

---

## 1. Micrographics

**What it is:** A design technique using tiny, detailed informational graphics and text as both decorative and functional elements. Originating from currency security printing (microtext, guilloche patterns, fine-line engraving on banknotes and passports), it has evolved into a major aesthetic trend for 2025-2026. Designers like Virgil Abloh and brands like Maison Margiela, Nike, and Nissan have adopted it as a defining design element rather than an afterthought.

### Key Visual Characteristics

- **Micro-text strings** -- Repeating tiny text (4-6px) that reads as texture from a distance but reveals hidden messages up close
- **Serial numbers and codes** -- Alphanumeric strings like `RFL-2026-0042`, `BATCH//07A` evoking authentication
- **Coordinate readouts** -- Latitude/longitude pairs, timestamps, data-like readouts suggesting precision
- **Guilloche patterns** -- The intricate, interlocking curved-line patterns found on banknotes
- **Fine-line grids and crosshairs** -- Registration marks, alignment crosses, dimensional callouts
- **Tiny schematic symbols** -- Circuit diagram notation, chemical structures, engineering notation
- **Barcode/QR-like decorative elements** and measurement scales

### Why They Work

They reward close attention (easter egg effect), imply technical depth and specialized knowledge, function as sophisticated texture at macro scale, carry connotations of legitimacy and authentication, and create a layered information hierarchy.

### Application to Hidden Marks

Card listings with micro-text borders containing set codes and rarity data; corner registration marks with crosshairs; guilloche-inspired backgrounds behind card images; section dividers made of fine geometric patterns; breadcrumbs styled as path coordinates (`ROOT > DECK_ARCHIVE > SET::ALPHA`); authentication badges with tiny guilloche borders and serial numbers. Color treatment: very low-contrast micro-text (dark gray on black, dim cyan on near-black) with occasional neon accent highlights.

---

## 2. Video Game Juice

**What it is:** The concept of providing abundant, delightful feedback to user interactions -- far more output than the input deserves. Popularized by game designers Martin Jonasson and Petri Purho, juice is the difference between a lifeless interface and one that feels physically satisfying and alive.

### Key Techniques

- **Squash and stretch** -- Objects deform on impact (button squashes on press: `scaleY: 0.95, scaleX: 1.05`)
- **Screen shake** -- Brief 2-4px random displacement for 100-200ms to convey impact
- **Particle effects** -- Bursts of sparks, confetti, energy motes on interaction
- **Easing functions** -- Spring/elastic curves with overshoot (`cubic-bezier(0.34, 1.56, 0.64, 1)`), back easing with pullback; linear motion feels dead, properly eased motion feels alive
- **Scale pops** -- Brief 1.0 -> 1.15 -> 1.0 on events like adding to cart
- **Sound design** -- Clicks pitched up for positive actions, layered sounds, combo sounds that escalate in pitch
- **Time manipulation** -- 50-100ms freeze on significant actions before animation plays; slow-motion for dramatic reveals
- **Combo/chain systems** -- Progressive feedback that intensifies with repeated actions

### Web CSS/JS Techniques

- **Spring animations** via Framer Motion (`type: "spring", stiffness: 300, damping: 20`) or CSS `cubic-bezier` with overshoot values
- **Magnetic buttons** -- Track mouse position, apply proportional `transform: translate()` as cursor approaches
- **Elastic scrolling** via Lenis/Locomotive Scroll + GSAP ScrollTrigger
- **Hover distortions** -- WebGL shader ripples, CSS filter transitions, SVG turbulence
- **Cursor trails** -- GSAP-powered trailing with elastic easing, particle trail following movement
- **3D card tilt** -- `transform: perspective(1000px) rotateX() rotateY()` based on cursor position

### Application to Hidden Marks

Cards tilt toward cursor in 3D with holographic shine tracking mouse position; "Add to Cart" with magnetic pull, squash on press, card miniature arcing into cart icon; pack opening with multi-stage animation (wobble -> tear -> staggered card reveal with hit-stop on rares); combo system where adding multiple cards triggers escalating feedback (`x2`, `x3`, `COMBO!`); navigation links with elastic hover; loading states as pulsing card-back animations.

### Recommended Stack

Framer Motion for React component animations, GSAP + ScrollTrigger for timelines, Canvas API for particles, Howler.js for audio.

---

## 3. Industrial Design Aesthetic

**What it is:** A visual style inspired by factories, heavy machinery, exposed infrastructure, and utilitarian construction. When fused with cyberpunk, it becomes darker and more dystopian -- think Blade Runner's factories, Alien's Nostromo corridors, or Cyberpunk 2077's Night City.

### Key Visual Elements

- **Rivets and bolts** -- Visible hex bolt fasteners at panel corners, rivet lines along edges
- **Metal plates and panels** -- Overlapping steel sheets with visible seams and welded joints
- **Grating and mesh** -- Diamond plate (checker plate), expanded metal mesh, perforated sheets
- **Warning stripes** -- Diagonal black-and-yellow hazard stripes on edges and borders
- **Exposed pipes/conduits** -- Visible infrastructure connecting sections
- **Weathered surfaces** -- Rust, patina, oil stains, paint chips, wear marks suggesting age and use
- **Stencil typography** -- Military/industrial broken letterforms; also label-maker text, stamped metal text, and monospaced terminal fonts
- **Gauges and meters** -- Circular gauges, bar meters, VU meters, pressure indicators as data visualization
- **Hazard symbols** -- Radiation, high voltage, biohazard pictograms as decorative elements

### Color Palette

| Category | Colors |
|----------|--------|
| **Darks** | Gunmetal (#2C3539), Carbon (#1a1a2e), Matte Black (#0d0d0d) |
| **Metals** | Brushed Steel (#71797E), Raw Iron (#48494B) |
| **Accents** | Hazard Yellow (#FFD700), Danger Red (#CC0000), Safety Green (#00CC44) |
| **Weathering** | Oxide Brown (#8B4513), Rust Orange (#B7410E) |
| **Indicators** | LED Green (#00FF41), Status Amber (#FFBF00) |

### CSS Implementation

Stacked `box-shadow` for embossed panel depth; SVG patterns for grating/diamond plate textures; `border-image` with repeating diagonal gradients for warning stripes; `text-shadow` for stamped-into-metal text effect; pseudo-elements for corner rivets and indicator lights; `clip-path` for angular chamfered panel shapes; SVG noise overlays for metal grain.

### Application to Hidden Marks

The site feels like a black-market tech dealer's terminal; product cards displayed on metal panels with riveted corners; rarity indicated by industrial color-coding (common = zinc gray, rare = danger red, mythic = hazard yellow with warning stripes); navigation as a control panel strip with indicator LEDs; cart styled as a "loadout manifest" with monospaced text; checkout steps as manufacturing process flow (`REQUISITION > VERIFICATION > PAYMENT > DISPATCH`); error states with warning stripe borders; footer as a "maintenance panel" with version numbers and system status.

### How All Three Combine (Micrographics + Juice + Industrial)

The three aesthetics layer together naturally: **Industrial** provides the macro structural language (panels, rivets, metal textures, warning stripes). **Micrographics** fill the fine detail layer (tiny text, coordinates, serial numbers in the spaces between industrial elements). **Game Juice** makes everything feel alive (spring-loaded hover states on riveted panels, gauge needles that animate smoothly, mechanical button press feedback with squash and particles).

---

## 4. Cards Against Humanity

**Site:** cardsagainsthumanity.com

**Overall Aesthetic:** The site embodies a deliberately **anti-corporate, irreverent aesthetic**. It rejects visual polish in favor of blunt honesty and self-deprecating wit. The design is stark, minimalist, and purposefully "undesigned" -- the provocative copywriting and brand personality carry the experience rather than visual flourish. They proudly display negative press quotes ("Bad" -- NPR, "Stupid" -- Bloomberg) as badges of honor, inverting conventional marketing logic entirely.

### Layout Structure

- **Header:** Minimal navigation with logo, Shop/About links, and cart counter. Purely functional, no visual embellishment.
- **Hero:** Large centered logo with the tagline "A party game for horrible people" set against a white background. Bold, declarative -- no rotating banners or hero images.
- **Product Sections:** Grid-based product displays with alternating copy placement. Products grouped into clear categories: Main Games, Expansions, Twists, Packs ($5 themed sets), and Other Stuff. Each section uses color-coded backgrounds from the product packaging.
- **FAQ Section:** Extensive Q&A section that functions as both support documentation and entertainment content.
- **Footer:** Organized into Shop, Info, and Find Us sections with newsletter signup.

### Typography

Sans-serif throughout -- clean, modern, utilitarian. No decorative or display fonts anywhere. Bold weights for headings, regular weights for body. The philosophy is that typography should be invisible -- the words themselves do the work.

### Color Palette

- **Primary:** Black text on white backgrounds. Extremely high contrast, stark, minimal.
- **Product-driven color:** Individual product boxes introduce color (green, yellow, purple packaging).
- **UI has virtually no color of its own** -- this mirrors the physical game (black cards, white cards).

### How They Sell

- **Anti-marketing as marketing:** No urgency tactics, no "limited time" pressure.
- **Free PDF downloads offered prominently:** Giving away the product for free builds enormous trust and paradoxically drives physical sales.
- **Product descriptions are single-line jokes.**
- **Pricing across 6 currencies** for international reach.

### Strengths & Weaknesses

**Strengths:** Brand consistency is flawless; free download builds goodwill; FAQ doubles as entertainment; simple product hierarchy makes shopping intuitive; international pricing reduces friction.

**Weaknesses:** Stark design may feel cold; heavy text reliance is not scannable; limited visual hierarchy on dense pages.

---

## 5. Exploding Kittens

**Site:** explodingkittens.com

**Overall Aesthetic:** **Bold, playful, yet premium.** A dark-mode aesthetic (#0F0F0F deep black paired with #FCF8EE warm cream) that reads as sophisticated and adult rather than childish. Illustration is the primary visual language, leveraging The Oatmeal's distinctive art style as a core brand asset.

### Typography

- **Headings:** "Epilogue" font, weight 800, uppercase, letter-spacing .02em. H1: 56px desktop / 36px mobile.
- **Body:** "Instrument Sans", weights 400 and 600. Base 16px.
- The uppercase bold Epilogue headings feel premium-fun -- not juvenile, not corporate.

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Deep Black | #0F0F0F | Primary backgrounds, text, button fills |
| Warm Cream | #FCF8EE | Backgrounds, button text (softer than pure white) |
| Charcoal | #2C3E50 | Secondary text |
| In-Stock Green | #2E9E7B | Status indicator |
| Sale/Error Red | #DE2A2A | Alerts, sale badges |
| Star Gold | #FFCF2A | Ratings |
| Label Blue | #405DE6 | Custom labels |
| Out-of-Stock Purple | #6F719B | Availability indicator |

Color serves function, not decoration. Every accent color has a purpose.

### Product Card Design

Product image with custom zoom cursor (SVG); title in uppercase Epilogue; price with regular/sale distinction; badges ("On Sale!" in red, "Out of Stock" in purple); star ratings via Okendo (28px stars); quick-add functionality; hover with shadow and background transitions.

### Buttons

- **Primary CTA:** Cream background (#FCF8EE), near-black text (#0F0F0F). 0px border-radius, 48-52px height, 24px horizontal padding, font-weight 600.
- **Secondary CTA:** Inverted -- black background, cream text.
- **Hover:** 2px box-shadow appears. Transition: opacity 0.4s ease-in-out.

### Animations

Restrained and purposeful -- button hover changes, CSS transitions, loading spin, modal fade-in, photo zoom cursor, Flickity.js carousel. No parallax, no scroll-triggered effects.

### Responsive Breakpoints

Phone (max 740px), Tablet (741-999px), Desktop (1200px+). All interactive elements 40-52px height minimum.

### Strengths & Weaknesses

**Strengths:** Black/cream palette is distinctive and cohesive; shipping transparency; review integration; multi-region support; strong typography pairing.

**Weaknesses:** Hero section loads dynamically; CTAs distinguished only by color inversion; no video-based game teaching.

---

## 6. Stonemaier Games

**Site:** stonemaiergames.com

**Overall Aesthetic:** **Premium, elegant, curator-like.** Positions the company not as a toy manufacturer but as a publisher of meaningful creative works. Refined minimalism with nature-inspired elements. A muted sage green background (#a5c868) with Wingspan bird illustration creates thematic connection to their games.

### Typography

System fonts throughout -- no custom typefaces. Prioritizes fast loading and accessibility. Small: 13px / Medium: 20px / Large: 36px / X-Large: 42px. Practical and readable but feels generic compared to competitors.

### Color Palette

- **Sage Green:** #a5c868 -- calming, natural
- **Dark Text:** #313131
- **Button Green:** #61a229 (hover: #4e8221)
- **CTA Orange:** #cf4e28 (hover: #a63e20)
- All solid colors, no gradients.

### Premium Product Presentation

Games positioned as "memorable, beautiful, fun" aesthetic objects. Each game has a full ecosystem of subpages: Rules & FAQ (with 2,000+ community comments), Design Diary, Media & Reviews, Digital Versions, Accessories & Promos, Dedicated Newsletter. Games are treated as living products with ongoing content.

### Blog Integration (Major Differentiator)

Substantial educational content: crowdfunding strategy, entrepreneurship, game design tutorials, shipping/fulfillment logistics, industry analysis. Positions Stonemaier as thought leaders and generates organic search traffic.

### Community Infrastructure

Per-game Facebook Groups, Discord, monthly newsletter, podcast, YouTube, Instagram/Bluesky, convention events. Rules pages with 2,167+ comments become community hubs.

### Purchase Flow

Separated architecture: main site (informational) + Shopify-powered store subdomain. Trust signals: "$10 Flat-Rate US Shipping", "20-Day Price Guarantee." Dual CTA pattern ("Buy" + "More Info") acknowledges the research phase.

### Strengths & Weaknesses

**Strengths:** Information architecture serves multiple audiences; multi-format rules support; blog generates authority; community linked to external platforms.

**Weaknesses:** 25+ titles with minimal curation; no recommendation engine; system fonts feel generic; info/store separation adds friction.

---

### Common Patterns Across All Three Card Game Sites

**Teaching Rules:** Scales with complexity. Simple games need minimal explanation. Mid-complexity uses instructions + reviews. Complex games require multi-format education (PDFs, videos, interactive tools, community Q&A, mobile apps).

**Showcasing Physical Products:** All three use high-quality product photography -- showing actual boxes/cards, not 3D renders. Authenticity matters. Game artwork does the visual heavy lifting.

**Building Community:** Community investment scales with game complexity. Party games need cultural presence; hobby games need support infrastructure.

**Converting Visitors to Buyers:**
- Simple/impulse games: Minimize friction, maximize personality, give the game away free.
- Mid-complexity: Standard e-commerce with social proof, reviews, badges, sale indicators.
- Complex/premium: Information-first, then commerce.

**Universal Design Principles:**
1. Product photography over lifestyle imagery or 3D renders
2. Strong, consistent brand voice in all copy
3. Mobile-responsive design
4. International awareness (multi-currency, multi-region)
5. Social proof (reviews, press quotes, community engagement)
6. Cart always visible in header
7. No aggressive popups or dark patterns -- card game audiences are savvy

---

## 7. Cyberpunk / Dystopian Design

### Origins and Foundational Works

**Blade Runner (1982)** established the visual vocabulary: perpetual rain with wet reflective surfaces that multiply neon light sources; towering megastructures with ground-level market squalor; giant holographic advertisements; dense architectural layering (Art Deco + industrial + Asian vernacular); film noir lighting with hard shadows and volumetric fog; corporate monoliths looming over street-level chaos.

**Akira (1988)** revolutionized through anime: iconic motorcycle light trails (red streaks), Neo-Tokyo's dense urban sprawl, military/surveillance imagery, explosive psychedelic color bursts against dark cityscapes, Japanese street culture.

**Ghost in the Shell (1995)** deepened the language: optical camouflage effects, neural interface imagery, digital "data dive" sequences with cascading characters (directly inspired The Matrix), reflections in water/glass/chrome as recurring motif.

### Key Visual Motifs

- **Neon on Dark**: The signature contrast. Dark backgrounds (#0a0a0f to #1a1a2e) with vibrant accent colors used sparingly.
- **Rain-Slicked Surfaces**: Wet surfaces create reflections. Web translation: glossy/reflective UI elements, subtle reflection effects beneath cards, glassmorphism with backdrop-blur.
- **Holographic Projections**: Semi-transparent glowing UI with slight transparency, chromatic aberration at edges, scan lines, flicker on interaction, cool cyan base color.
- **Corporate Signage in CJK Characters**: Japanese katakana, Chinese hanzi as decorative background elements at low opacity and large scale. Used as atmospheric texture, not meant to be "read."
- **Dense Urban Layering**: Multiple planes of visual depth. Web translation: layered z-index, parallax scrolling, overlapping sections.
- **Surveillance Imagery**: Corner bracket framing, crosshair elements, red recording indicators. Web UI: corner bracket decorations on cards, "scanning" hover animations, blinking status indicators.
- **Glitch Art**: Horizontal displacement, chromatic aberration (RGB offset), noise/static overlays. CSS: pseudo-elements with `clip-path: inset()` and `steps()` timing. Use on hover/interaction only for accessibility.
- **Data Streams**: Falling/scrolling characters, binary code overlays, terminal-style text.

### Specific Textures

- **Corrugated Metal**: Ribbed panels with visible rivets, peeling paint revealing rust
- **Rust**: Orange-brown oxidation concentrated at edges and joints (5-15% opacity overlays)
- **Grime Over Chrome**: Clean chrome smeared with oil/grease -- the "high tech, low life" texture
- **Cracked Screens**: Spider-web fracture patterns, color distortion along crack lines
- **Cables and Wiring**: Exposed infrastructure, circuit board patterns
- **Concrete/Brutalist**: Raw unfinished surfaces -- the "low life" base that neon illuminates

### Typography

| Style | Examples | Web Use | Conveys |
|-------|----------|---------|---------|
| Monospace | IBM Plex Mono, JetBrains Mono, Fira Code | Data displays, prices, code-like elements | Technology, surveillance, data processing |
| Condensed Sans-Serif | Barlow Condensed, Oswald, Bebas Neue | Headlines, navigation, display text | Urgency, density, industrialism |
| CJK Decorative | Noto Sans JP | Background texture, branding accents | Globalism, otherness, cultural layering |
| Glitch/Distorted | CSS text-shadow + clip-path animations | Hover states, loading indicators | Digital corruption, imperfection |
| Angular/Geometric | Rajdhani, Orbitron, Audiowide | Logos, hero text, section headers | Futurism, precision, corporate branding |

### Color Combinations

**Primary Cyberpunk -- Cyan/Magenta on Black:**
- Background: `#0a0a0f` (near-black, slight blue) -- NEVER pure `#000000`
- Primary accent: `#00e5ff` (electric cyan) or `#00fff0` (aqua)
- Secondary accent: `#ff0055` (hot magenta) or `#ff2d6b`
- Tertiary: `#bd00ff` (electric purple)
- Text: `#e0e0e0` (light gray, not pure white)

**Amber Terminal:** Background `#0d0d0d`, Primary `#ffa000` (amber), Text `#33ff33` (green terminal)

**Red Warning/Alert:** Background `#0a0008`, Primary `#ff1744` (warning red)

**Midnight Firewall (Recommended for this store):**
- Background: `#151c3c` (deep navy) to `#050609` (near-black)
- Cyan: `#00e5ff`, Amber: `#ffa000`, Red: `#ff1744`

**Key rules**: Never pure white or pure black. Limit neon to 2-3 consistent accents. Large neon areas cause eye fatigue -- keep them as accents only.

### Web Design Translation

**Layout**: CSS Grid with overlapping elements, asymmetric offsets, HUD-style corner brackets framing cards/images, diagonal section dividers, content panels styled as "terminal windows."

**CSS Effects (Performant):**
- `backdrop-filter: blur()` for holographic panels
- Multi-layer `text-shadow` for neon glow: `0 0 7px #00e5ff, 0 0 10px #00e5ff, 0 0 21px #00e5ff`
- Scanline `::before` with repeating linear-gradient (1-2px lines)
- Glitch via `@keyframes` + `clip-path: inset()` + `steps()` at 60fps
- Noise overlay via small tiling SVG at low opacity
- `mix-blend-mode` for chromatic aberration on pseudo-elements

**Interaction**: Hover glitch/flicker, focus neon glow, "scanning" load animation, `prefers-reduced-motion` respect for accessibility.

**Framework**: CYBERCORE CSS provides 6 built-in effects (Glitch, Neon Border, Scanlines, Noise, Datastream, Text Glow).

---

## 8. Graffiti as a Design Element

### Core Styles and Digital Translations

**Tagging**: Quick stylized signature, fluid connected letters, single color, drips from speed. Web use: accent text for quotes, signature-style hover effects, decorative edge elements.

**Throw-ups**: Bubble letters in 2-3 colors (fill + outline). Web use: bold rounded display text for section headers, promotional banners.

**Pieces (Masterpieces)**: Full-color detailed works with 3D effects. Web use: hero graphics, brand identity, special edition product reveals.

**Stencil Art (Banksy-Style)**: Clean high-contrast imagery from cutouts, 1-3 colors, sharp edges with imperfect spray application. Web use: category icons, "limited edition" stamps, illustrative section elements, themed badges.

**Wheat-Paste Posters**: Paper posters layered over time, older posters visible through tears, natural distressing/peeling. Web use: promotional banners, "peeling" reveal animations on hover, layered collage backgrounds.

### Visual Characteristics for Digital Use

**Spray Paint Textures**: Dot diffusion pattern (heavier center, lighter edges), overspray halos, drip marks. Implementation: PNG overlays at 5-20% opacity, spray-pattern borders, particle effects on hover.

**Drip Effects**: Paint running downward in varying thickness/length. Implementation: SVG drip shapes as section dividers, decorative drips hanging from nav bars or card borders, animated via `transform: scaleY` with `transform-origin: top`. Key tip: drips must connect to other elements -- isolated drips look amateur.

**Distressed/Peeling Surfaces**: Layers worn away revealing underlying brick, metal, older paint. CSS: `mix-blend-mode: multiply` or `screen` with grunge texture overlays.

**Layered Urban Textures**: Visual archaeology (brick > paint > poster > graffiti > sticker > more paint). Implementation: parallax layers at different scroll speeds, z-stacked backgrounds with varying opacity.

### Specific Web UI Techniques

- **Texture Overlays**: Subtle grunge/spray texture via CSS `background-image` with `mix-blend-mode`. Opacity 5-15%.
- **Decorative Elements**: Spray splatters near headlines/CTAs, stencil-style category icons, drip SVGs as card bottom borders, hand-drawn arrows/circles, paint-stroke active navigation states.
- **Section Dividers**: Spray paint stroke dividers, drip border rows, torn paper edges (SVG clip-path), stencil pattern bands.
- **Hover Effects**: Spray texture appears behind buttons, small graffiti "tag" in card corners, paint-stroke underline animates in on links.
- **Typography**: Graffiti fonts ONLY for display text (headlines, prices, promotional). Body text stays clean sans-serif.

### Tasteful vs. Overdone

**Tasteful**: Graffiti as supporting texture not primary visual; 1-2 techniques per page; subtle overlays that add grit without hurting readability; graffiti typography limited to headlines; color restraint; elements that feel "discovered"; consistent application. Brand examples: Supreme, Palace, Obey.

**Overdone**: Every surface covered; graffiti fonts for body text (unreadable); too many competing styles; random splatters unrelated to layout; elements obstructing navigation; no contrast between textured and clean areas.

**The Rule of Contrast**: Graffiti has the most impact juxtaposed against clean, structured design. A perfectly aligned grid with one spray-painted divider is far more powerful than an entirely graffiti-covered page. The rebellious energy comes from the contrast between order and chaos.

### Cyberpunk + Graffiti Fusion

Both are rooted in urban counter-culture and visual layering:
- Stencil-style "limited edition" / "sold out" badges (sprayed on)
- Spray texture overlays on dark backgrounds add gritty urban layer beneath neon
- Drip effects in neon colors (cyan drips, magenta drips) merge both aesthetics
- Wheat-paste style event/promotion announcements
- Tagging-style decorative elements in flavor text sections
- Distressed metal/industrial textures provide the "low life" grime cyberpunk requires

---

## 9. E-Commerce Best Practices

### Product Page Layout

**Hero Image / Product Photography:**
- 93% of consumers cite visual appearance as the key deciding factor
- For a card game: show card art prominently, physical card with packaging, card in play context, close-up of foil/detail effects
- Multiple images: front, back, in-hand scale, in-collection context
- Dark background photography works extremely well for cyberpunk theme (products glow against dark)

**Price Placement**: Immediately visible above the fold, near title and CTA. Sale prices: original crossed out, sale price in accent color. All costs upfront -- 48% abandon over unexpected costs.

**CTA Button Design**: Most visually prominent element on page. For cyberpunk: neon-glow border, high contrast, minimum 48x48px touch target. Action-oriented text ("Add to Cart," "Grab This Card"). Sticky/fixed on mobile.

**Trust Signals**: Products with 5+ reviews convert 270% better. Place trust signals NEAR payment/CTA area. Key signals: SSL badge, payment method icons, return policy, shipping info, review count/stars. For card game: community endorsements, card condition guarantees, secure packaging assurance.

**Information Architecture**: Avoid horizontal tab layouts (worst-performing in testing). Use vertical accordion or long-scroll with anchor links. Hierarchy: Image > Title > Price > CTA > Short description > Reviews > Detail > Related products.

### Checkout Flow

**Cart Abandonment**: 70% of carts are abandoned. Drivers: Unexpected costs (48%), Forced account creation (24%), Trust deficit (18%), Payment friction (13%).

**Guest Checkout**: 63% abandon if unavailable. Make it the default path. Shift account creation to confirmation page ("Save info for next time? Enter a password:").

**One-Page Checkout**: Reduces abandonment by 20%. If multi-step: clear progress indicator. Minimum: Shipping > Payment > Confirmation. "Secured by Stripe" more credible than generic padlock graphics.

**Pricing Transparency**: 39% abandon when costs appear late. Show shipping estimate on product page. Show tax estimate based on location. Running total visible always.

### Cart Design

**Mini-Cart**: Slide-out panel on item add (no full page nav). Shows thumbnail, name, quantity, price, subtotal. Quick quantity adjustment, remove button. "Continue Shopping" + "Checkout" CTAs. Cyberpunk styling: neon border, scanline texture.

**Persistent Cart**: Header icon with count badge. Persists across sessions (localStorage + server sync). Accessible from any page. Mobile: bottom-fixed cart bar when items present.

**Upsells**: "Complete your deck" for card games, "Players also bought" in cart. Max 3-4 suggestions. Bundles at discount vs. individual pricing.

### Mobile Commerce

- 73% of e-commerce traffic is mobile (2025-2026)
- Desktop converts at ~2x mobile rate -- massive improvement opportunity
- 53% abandon sites taking >3 seconds

**Mobile Patterns**: Thumb-zone CTAs (bottom 1/3), bottom nav bar, swipeable image galleries, sticky "Add to Cart," bottom-sheet filters, large touch targets (48x48px minimum), auto-suggest search, one-tap payment (Apple Pay, Google Pay).

### Social Proof

**Reviews**: 5+ reviews = 270% better conversion. Stars near title above fold. Text + photo/video reviews. Distribution chart. Filter by rating/relevance/recency. Respond to negatives publicly.

**User-Generated Content**: Customer photos of cards in use, social media tagged purchases, community deck lists, tournament results.

**Indicators**: "X people viewing" (if genuine), "Y sold recently," Bestseller/Popular badges, staff picks.

### Urgency/Scarcity

**Legitimate**: Low stock warnings (when true), limited edition counters ("487/500 remaining"), pre-order deadlines, sale countdowns, seasonal availability.

**Avoid (Manipulative)**: Fake timers that reset, artificial stock counts, fabricated "someone bought" notifications. These erode trust and may violate regulations.

### Loading Performance

**Core Web Vitals Targets**: LCP < 2.5s, INP < 200ms, CLS < 0.1.

**Techniques**: Lazy loading below-fold images, responsive `srcset`, WebP/AVIF formats (30-50% smaller), critical CSS inlined, CDN for static assets, skeleton screens (better than spinners), preload critical fonts/hero images, service worker caching.

**Cyberpunk-Specific**: Textures as small tileable SVGs not large PNGs, neon glow via CSS not images, glitch on interaction only, backgrounds via CSS gradients, `prefers-reduced-motion` media query for animation opt-out.

### Accessibility

**WCAG Essentials**: Minimum 4.5:1 contrast for text -- CRITICAL for neon on dark (test cyan on navy). Keyboard navigation (Tab, Enter, Escape). Visible focus indicators (neon glow works well). Alt text on all product images. Form labels (not placeholder-only). ARIA labels on icon buttons. No color-only information conveyance.

**Dark Theme Specifics**: Never pure black backgrounds (use #121212 or #1a1a2e -- reduces halation for astigmatic users). Text slightly off-white (#e0e0e0 to #f0f0f0). Increase font weight slightly. Increase line-height (1.6-1.8). Test neon accents against dark for WCAG compliance. Consider light mode toggle.

### Trust Builders vs. Trust Destroyers

**Builders**: Professional consistent design, clear contact info, visible return policy, secure payment badges near payment fields, real reviews, fast load times, clear product photography, transparent pricing, social media links, professional copywriting.

**Destroyers**: Hidden shipping costs (#1 driver), forced account creation, hidden guest checkout, poor mobile experience, broken images/layout, no SSL, unclear return policy, no/fake reviews, aggressive popups, complex multi-page checkout, no payment security indication, poor error handling, broken search.

### The 80/20 Rule

For a dark cyberpunk card game e-commerce store: **80% clean functional e-commerce / 20% cyberpunk-graffiti atmosphere**. That 20% creates 80% of the memorable impression. Every decorative element must enhance, not obstruct, the shopping experience.

---

## 10. Marathon (Bungie)

**Overall Aesthetic:** Marathon's visual identity is defined by what Art Director Joseph Cross calls **"Graphic Realism"** -- a deliberate contrast to photorealism. Two pillars:
- **Pillar 1 (Graphic):** Simplified/deconstructed universal design language, strong graphic design and color statements, limited materials
- **Pillar 2 (Realism):** Realistic proportions and scale, implied functional detail, a generally grounded world

The world aesthetic is best described as **Y2K Cyberpunk mixed with Acid Graphic Design Posters**. It amplifies the juxtaposition of the familiar and the futuristic.

### Key Design Influences

The Designers Republic (legendary Sheffield studio behind Wipeout's visual identity); Wipeout (PS1-era clean geometric futurism); Ghost in the Shell; Mirror's Edge (clean white environments with bold color accents); Aeon Flux; Alberto Mielgo (Spider-Man: Into the Spider-Verse); Akira; Formula 1 / MotoGP (livery design, sponsor graphics, racing iconography); Metal Gear Solid 2 (tactical/military UI language).

### Typography

- **Logo font (classic):** Modula Tall by Emigre Inc. -- extremely condensed sans-serif where diagonal strokes are virtually eliminated
- **New Marathon:** Custom display typeface -- bold, geometric, tightly tracked
- **UI typography:** Monospace and utilitarian fonts for data readouts
- **Overall approach:** Bold condensed sans-serifs with utilitarian/industrial character. Text treated as a graphic design element -- echoing The Designers Republic approach where typography IS the art.

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Acid/Lime Green | #c2fe0b | Signature color -- character outfits, UI elements, signage |
| Electric Cyan | #01ffff | Secondary accent, digital interface elements |
| Hot Red | #ff0d1a | Danger, alerts, combat indicators |
| Dark Navy/Gunmetal | #29324f | Backgrounds, environments, structures |
| Deeper Green | #59b41d | Environmental, secondary |

Strong, saturated, contrasting colors with hard edges. Little blending or gradients.

### UI/UX Patterns

- Glitchy data readout overlays and digital corruption effects
- Utilitarian labeling: "CAUTION: HIGH VOLTAGE" stickers, boldly labeled access panels
- Flat color blocking: Large areas of saturated flat color with hard edges
- Geometric iconography: Bold, clean, angular symbols
- Neon-acid palettes against dark/industrial backgrounds

### What Makes It Distinctive

The "Graphic Realism" concept -- graphic design applied to 3D game environments. The acid graphic poster aesthetic applied to a AAA game is unprecedented. The Designers Republic influence brings 1990s-2000s rave/electronic music visual culture into a modern game. The blend of racing livery graphics with cyberpunk creates athletic, kinetic energy. The flat, saturated color language makes it instantly recognizable in screenshots.

---

## 11. MORK BORG

**Site:** morkborg.com

**Overall Aesthetic:** MORK BORG is an **art-punk, doom metal, apocalyptic medieval** tabletop RPG whose visual identity is as much the product as the rules themselves. Designer Johan Nohr treats the entire book as a piece of visual art -- every spread designed like a poster. The aesthetic channels **punk zine culture, extreme metal album art, Dadaist typography experiments, and medieval woodcut prints**. The core paradox: a bleak, dying world portrayed in **screaming neon yellow and pink** rather than expected dark/muted tones. The contradiction IS the design statement.

### Key Design Influences

Underground/arthouse zine design (primary inspiration); extreme metal aesthetics (death metal logos, doom metal atmosphere); early 20th century avant-garde typography: Marinetti (Futurism), Zdanevich/Iliazd (Dada), Tzara (Dada); medieval woodcut prints; punk culture -- DIY ethos, intentional roughness, anti-establishment design.

### Typography

MORK BORG uses **over 100 different typefaces** in its 96-page book:
- Blackletter/Gothic/Old English scripts are the signature category -- headings, titles, atmospheric text
- Typography is treated as illustration: Nohr "paints with letters"
- Individual letters placed "by hand" -- slightly tilted, skewed, creating something tactile and homemade
- Includes deliberately "bad" fonts (Comic Sans, Papyrus) as an experiment in redemption through context

**Website typography:** Druk Wide and Druk Condensed (ultra-bold industrial display), Lo-Res 22 Serif (pixel/bitmap aesthetic), Calling Code (monospace-inspired utilitarian), Georgia (serif body text creating formal/crude tension).

### Color Palette

- **Rich Black** -- dominant background
- **Shocking Yellow** (~#ffe800) -- signature accent, interactive elements, highlights
- **Shocking Pink/Magenta** (~#ff40b4) -- secondary accent, hover states, borders
- **White** -- primary text color against dark backgrounds
- **Achromatic Grays** -- supporting elements
- **Occasional Muted Blue** -- very rare, for chromatic compartmentalization
- **Brooding Reds** -- deployed selectively for maximum emotional impact

### Layout & Composition

- No grid system for most of the book -- "the blank page, an empty canvas"
- Grid appears ONLY in adventure sections and rules summaries -- deliberate two-system approach (chaos for atmosphere, structure for usability)
- Every spread treated as a poster -- complete visual compositions
- Reading patterns respected: Despite apparent chaos, layout follows Western left-to-right, top-to-bottom movement
- Negative space is meaningful: Sparse content areas stay empty. Space conveys information.

### Website Translation

Black backgrounds, yellow (#ffe800) interactive elements, pink (#ff40b4) hover states. Industrial typography (Druk Wide/Condensed, Lo-Res 22 Serif). Hover states use color inversion (yellow becomes blue). Deliberately crude, anti-AAA polish. Minimal ornamentation. Content-first hierarchy.

### What Makes It Distinctive

100+ typefaces in one book is unprecedented. The poster-per-spread approach makes every page a visual event. The yellow/pink/black punk palette for a grimdark dying world is an inspired contradiction. Typography AS illustration. The design spawned an entire ecosystem of "BORG" games following Nohr's visual template.

---

## 12. Cyberpunk 2077

**Overall Aesthetic:** Cyberpunk 2077's visual identity embodies a **rapidly deteriorating, dangerous future masked by hypnotically bright neon lights**. The UI is built on the in-universe **"Neomilitarism"** style -- cold, threatening elegance with practical luxury. Catchphrase: "substance over style."

### Typography

- **Primary - Rajdhani:** Used for the entire in-game UI in Regular, Medium, Semi-Bold, and Bold weights. A squared, geometric sans-serif with "technical or futuristic" appearance. Also appears diegetically on in-game screens.
- **Secondary - Orbitron:** Non-important, decorative UI text. Geometric, squared futuristic display face.
- **Marketing - Refinery** (headlines) and **Blender** (headlines + body, also diegetic in-world).
- **Logo:** Custom hand-drawn letterforms -- slightly slanted, thick lines, angular shapes, elongated tails with softened ends. "2077" in thin sharp neon-blue lines.
- Three of four fonts appear both in the UI AND in-world, creating seamless world-building through typography.

### Color Palette (UI Core)

| Color | Hex | Usage |
|-------|-----|-------|
| Pure Black | #000000 | Dominant background |
| Crimson Red | #c5003c | PRIMARY interface color (Neomilitarism) |
| Dark Red | #880425 | Secondary |
| Neon Yellow | #f3e600 | Signature brand color, marketing, highlights |
| Cyan/Turquoise | #55ead4 | Tech elements, data readouts |

**The Red Controversy:** Using RED as the default UI color was a bold, deliberate decision against all convention. Red normally communicates malfunction, warnings, and danger, so using it as the BASELINE makes everything feel slightly hostile. This IS the Neomilitarism philosophy made tangible.

### UI/UX Patterns

**HUD Structure:**
- Curved by shader effects -- subtly warped as if projected on a spherical surface, reinforcing V's cyberoptic augmented reality overlay
- Dynamic minimalism: Health only displays when damaged. Stamina appears during depletion.
- Contextual adaptation: Different layouts for combat, armed-no-combat, and unarmed states.

**Glitch Effects (the signature technique):**
- **Chromatic Aberration / RGB Channel Split:** Cyan shifts left, red/magenta shifts right
- **Digital Signal Failure:** Clip-path animations slice through text and UI randomly
- **Scanline Overlay:** Repeating horizontal lines via repeating linear gradients
- **Jitter Animations:** `steps()` timing function creates robotic, jerky motion
- **Data Corruption:** Random pixel displacement, text scrambling, visual "snow"

**Holographic / Glassmorphic Effects:** Semi-transparent panels with layered blurs and highlights. Glowing text shadows and outlines. Elements appear to float in 3D space.

### What Makes It Distinctive

Red as default UI color subverts every convention. Diegetic UI integration -- same fonts in interface AND in-world screens. The curved HUD shader makes the interface feel projected by cyberoptics. The glitch aesthetic is systematic, not random. Neon yellow as brand identity is bold and immediately recognizable. The tension between sleek corporate design and entropic decay mirrors the game's thematic tension. Rajdhani as UI font gives a "near-future institutional" quality.

---

### Comparative Summary: Marathon vs. MORK BORG vs. Cyberpunk 2077

| Element | MARATHON | MORK BORG | CYBERPUNK 2077 |
|---------|----------|-----------|----------------|
| **Core Aesthetic** | Y2K Acid Graphic Realism | Art-Punk Doom Metal Zine | Neon Noir Corporate Decay |
| **Color Strategy** | Saturated flat colors, hard edges | Limited palette (yellow/pink/black) | Dark ground + neon accents (yellow/red/cyan) |
| **Typography** | Industrial condensed sans-serif, monospace data | 100+ typefaces, typography as illustration | Rajdhani (geometric sans), glitch-degraded text |
| **Layout** | Clean geometric grids, racing livery graphics | Poster-per-spread, anti-grid chaos | Curved diegetic HUD, contextual minimalism |
| **Signature Effect** | Digital glitch on flat color | Hand-placed letters, woodcut prints | RGB chromatic aberration, scanlines |
| **Design Philosophy** | "Graphic Realism" | "Each spread is a poster" | "Substance over style" (Neomilitarism) |

---

## 13. Synthesis: Applying It All to Riffle Square Cut

### Design DNA

The Riffle Square Cut website should feel like a **cyberpunk black-market terminal** where you're browsing contraband card decks in a dystopian underground. The core identity draws from:

- **Cyberpunk 2077** for the HUD-like interface language, glitch effects, and neon-on-dark palette
- **Marathon** for the flat color blocking, geometric iconography, and "Graphic Realism" approach to typography
- **MORK BORG** for the audacity of contrast (vibrant neon against dark themes), typographic experimentation, and punk energy
- **Industrial aesthetic** for structural elements (metal panels, rivets, warning stripes, gauges)
- **Micrographics** for the detail layer that rewards close inspection -- tying directly into the card game's "hidden marks" concept

### Color System

**Primary palette** aligned with PROJECT.md (black, red, white) enhanced with cyberpunk depth:

| Role | Color | Hex |
|------|-------|-----|
| Background (base) | Near-black | #0a0a0f |
| Background (elevated) | Dark navy | #151c3c |
| Primary accent | Danger red | #ff1744 or #c5003c |
| Secondary accent | Electric cyan | #00e5ff |
| Text (primary) | Off-white | #e0e0e0 |
| Text (secondary) | Medium gray | #71797E |
| Success/confirmation | LED green | #00FF41 |
| Warning | Status amber | #FFBF00 |
| Highlight (rare/special) | Neon yellow | #f3e600 |

Never pure black (#000000) or pure white (#ffffff). Limit neon accents to 2-3 per view.

### Typography Stack

| Role | Font | Style |
|------|------|-------|
| Display/hero | Rajdhani or Barlow Condensed | Uppercase, geometric, angular |
| UI/navigation | Condensed sans-serif | Bold weight, tight tracking |
| Body text | Clean sans-serif (Instrument Sans or similar) | Regular weight, 1.6-1.8 line-height |
| Data/prices/codes | JetBrains Mono or IBM Plex Mono | Monospace -- evokes terminal/surveillance |
| Micro-text decoration | Monospace at 4-6px | Low contrast, texture function |

### Interaction Model

Following the **juice** philosophy with cyberpunk flavor:

- **Cards**: 3D tilt toward cursor with holographic shine; magnetic hover pull
- **Add to Cart**: Squash animation on press, card miniature arcs into cart icon, particle burst
- **Navigation**: Elastic hover with neon glow focus indicators
- **Loading**: Pulsing card-back animations, glitch transitions between pages
- **Combos**: Escalating feedback for bulk actions (adding multiple items)
- **Sound**: Optional subtle click/confirmation sounds via Howler.js
- **Respect**: `prefers-reduced-motion` disables all non-essential animation

### Structural Language

Panels styled as industrial metal plates with:
- Corner rivets (pseudo-elements)
- Micro-text borders with set codes and serial numbers
- HUD-style corner brackets framing product images
- Warning stripe accents on error states
- Gauge/meter visualizations for inventory and stats in the employee dashboard
- Scanline overlays at very low opacity

### E-Commerce Foundation

The **80/20 rule** applies: 80% clean, functional, conversion-optimized e-commerce / 20% cyberpunk atmosphere that creates 100% of the memorable impression.

**Non-negotiables:**
- Product photography is hero (not 3D renders)
- Price visible above fold near CTA
- Guest checkout as default path
- One-page checkout with Stripe trust signals inline
- Mini-cart slide-out (no page navigation)
- Mobile-first: sticky CTA, thumb-zone layout, 48px touch targets
- Core Web Vitals: LCP < 2.5s, INP < 200ms, CLS < 0.1
- WCAG 4.5:1 contrast on all text (test neon on dark carefully)

### Unique Opportunities for Hidden Marks

- **Micrographics as easter eggs**: Tiny text throughout the site containing hidden messages, game lore, or discount codes -- directly reinforcing the "hidden marks" brand concept
- **Pack opening ceremony**: Multi-stage animation for product reveals (wobble -> tear -> staggered card reveal)
- **Authentication aesthetic**: Product cards styled with guilloche borders, serial numbers, and registration marks -- evoking the security printing that inspired micrographics, while implying collectible value
- **The "loadout manifest" cart**: Checkout styled as a requisition process (`REQUISITION > VERIFICATION > PAYMENT > DISPATCH`)
- **Industrial rarity system**: Common = zinc gray, rare = danger red, mythic = hazard yellow with warning stripes
- **Stencil badges**: "LIMITED EDITION" and "SOLD OUT" as spray-stencil overlays on product cards
- **Neon drips**: Section dividers using SVG drip shapes in accent colors

### Technical Implementation Notes

- **Animations**: Framer Motion for React components, GSAP + ScrollTrigger for scroll-driven timelines, Canvas API for particles
- **Textures**: Small tileable SVGs (not large PNGs) for grunge/metal/noise overlays
- **Neon glow**: CSS `text-shadow` / `box-shadow` stacking -- no images needed
- **Glitch effects**: CSS `@keyframes` + `clip-path: inset()` + `steps()` timing -- compositor thread, 60fps
- **3D card viewer**: React Three Fiber, built programmatically from 2D art (per PROJECT.md)
- **Audio**: Howler.js for optional interaction sounds
- **Performance**: Lazy load below-fold, WebP/AVIF images, critical CSS inlined, service worker caching, skeleton screens

---

## Sources

### Micrographics & Industrial Design
- How Micro-Graphics Went from an Afterthought to an Aesthetic (openallhours.co)
- Graphic Trends for 2026 -- It's Nice That
- Security Printing -- Wikipedia
- Banknote Security Features -- National Academies Press
- Corporate Grunge -- Aesthetics Wiki
- Neubrutalism Web Design Trend (bejamas.com)
- Cyberpunk Design Trends & Aesthetics (brainstormprojects.studio)

### Game Juice & Animation
- Juicy UI: Why the Smallest Interactions Make the Biggest Difference (Medium)
- CSS Animations for Game Juice (mccormick.cx)
- Juice -- Brad Woods Digital Garden
- Designing for a Juicier Web (userjourneys.com)
- Squeezing More Juice Out of Your Game Design (gameanalytics.com)
- Game Juice CSS Snippets (chr15m.github.io)
- Making Gameplay Irresistibly Satisfying Using Game Juice (thedesignlab.blog)
- Juice in Game Design -- Blood Moon Interactive
- Awwward-winning Animation Techniques (Medium/Design Bootcamp)
- Spring Easing Library (github.com/okikio)

### Card Game Sites
- cardsagainsthumanity.com
- explodingkittens.com
- stonemaiergames.com / store.stonemaiergames.com

### Cyberpunk / Dystopian / Graffiti
- Blade Runner (1982), Akira (1988), Ghost in the Shell (1995)
- CYBERCORE CSS framework
- Supreme, Palace, Obey brand references

### E-Commerce
- Baymard Institute checkout usability research
- Core Web Vitals documentation (web.dev)
- WCAG 2.1 accessibility guidelines

### Game/Brand References
- Marathon (Bungie) -- Joseph Cross art direction, The Designers Republic influence
- MORK BORG (Ockult Ortmastare Games) -- Johan Nohr design, morkborg.com
- Cyberpunk 2077 (CD Projekt Red) -- Neomilitarism UI design
