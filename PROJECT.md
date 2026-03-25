# Riffle Square Cut — Project Documentation

## Overview

Riffle Square Cut is an e-commerce website for selling **Hidden Marks**, a card game. Beyond the storefront, the site serves as a full business operations platform with customer accounts, business (B2B) accounts, employee dashboards, and promotional systems. The site's design is dark, futuristic, and highly interactive — inspired by dystopian/cyberpunk aesthetics with game-like "juice" elements throughout.

---

## Tech Stack

- **Framework:** React / Next.js
- **Payments:** Stripe
- **Hosting:** Currently on Squarespace (migrating — needs new hosting recommendation; Vercel or Render are strong candidates for Next.js)
- **Domain:** Already owned (currently on Squarespace)
- **Email:** Transactional email service TBD (SendGrid, Resend, or AWS SES recommended)
- **Database:** TBD (PostgreSQL recommended)
- **Real-time chat:** TBD (WebSocket-based, potentially with AI integration)
- **Maps:** TBD (Google Maps or Mapbox)
- **3D rendering:** Three.js or React Three Fiber (for card viewer)
- **Mobile:** Fully responsive web — no native app planned

---

## Products & Store

### Current Product
- **Hidden Marks** — a card game with 20–50 unique card designs
- Card art and logo assets exist; brand guidelines are still being finalized

### Future Products
- The store should be architected to support multiple products (expansions, accessories, merch) even though only Hidden Marks is available at launch

### Pricing
- Retail price: TBD
- Business/bulk pricing uses a **tiered discount** structure (e.g., 10+ units = X% off, 50+ units = Y% off — exact tiers TBD)

### Shipping
- **US only**
- **Flat rate** shipping fee
- Business accounts get **free shipping**

### Tax
- Automatic sales tax calculation: TBD (Stripe Tax or TaxJar are options)

---

## User Roles & Authentication

### Authentication Method
- **Magic link / passwordless** — users sign in via a link sent to their email, no password required

### User Types

There are three account types, all accessed from the same sign-in page with a role selector:

#### 1. Customer
- Signs up with email
- Can browse, purchase, view past orders, view past help requests
- Can participate in giveaways, referrals, and promotions

#### 2. Business
- Signs up with email + **uploads a resale certificate**
- Account requires **manual approval by an employee** before purchasing is enabled
- Once approved, can:
  - Purchase at tiered bulk discounts
  - Get free shipping
  - Receive invoices
  - View order history

#### 3. Employee
- Accounts are **created by an admin** (no self-registration)
- **All employees have equal permissions** (no role hierarchy)
- Access to the employee dashboard (see below)

---

## Pages & Features

### 1. Home Page
- Hero section with **floating 3D cards** (animated, interactive)
- Clear call-to-action to purchase Hidden Marks
- Design elements: geometric shapes, HUD-like overlays, micrographics, animations
- Card design elements woven throughout

### 2. Product / Store Page
- Product details for Hidden Marks (and future products)
- **3D card viewer** — users can rotate and inspect card designs in 3D
  - Built programmatically from 2D card art (front/back images), not pre-made 3D models
- Add to cart, checkout flow via Stripe
- Quantity selection, shipping info, order summary

### 3. Blog
- **Built-in CMS** — employees write and edit posts from an admin panel on the site
- Blog listing page with posts
- Individual post pages
- Features TBD: categories/tags, search, social sharing, comments

### 4. Interactive Map
- Map showing retail shops that carry Hidden Marks
- **Employee-managed** — locations are added/edited/removed from the employee dashboard
- Map pins with store name, address, and any relevant details

### 5. Tutorial Page
- **Interactive walkthrough** — step-by-step guided experience where users interact with virtual cards to learn the game
- Game rules and mechanics: TBD (to be provided later)

### 6. Contact Form
- Standard contact form for customer inquiries
- Submissions are visible to employees in the dashboard

### 7. Chat Bubble (Every Page)
- Persistent chat widget on every page
- **Hybrid system:**
  - When employees are online: **live chat** in real-time
  - When employees are offline: **AI chatbot** attempts to answer common questions about the game and orders
  - If AI can't resolve the issue: offers a **"leave a message" form** that creates a ticket
- Chat history is tied to the user's account and visible in their profile

### 8. Customer Account Page
- View past orders
- View past help requests / chat history
- Account settings

### 9. Weekly Giveaway Page
- **Button click race** — a page goes live at a set time each week
- First logged-in user to click the button wins
- Must have an account to participate
- Rules TBD: one win per account ever? Cooldown period? What's being given away?

### 10. Easter Eggs
- Hidden interactive elements scattered throughout the site
- Discoverable by curious users (click sequences, hidden pages, subtle visual cues, etc.)
- Rewards TBD (could be discount codes, badges, or just fun discoveries)

---

## Employee Dashboard

### Orders Management
- View all current/pending/completed orders (both online and in-person)
- Order details, status updates, fulfillment tracking

### Help Requests
- View pending customer help requests from chat
- Respond to tickets
- Live chat interface when online

### Stats & Analytics (Full Dashboard)
- **Sales metrics:** Revenue, orders per day/week/month, top products, conversion rates
- **Operations:** Inventory levels, pending orders, help request volume, giveaway status
- **Trends:** Charts and graphs for key metrics over time

### In-Person Sales Tracking
Employees can log sales with the following fields:
- Product
- Quantity
- Payment method
- Type of sale (in-person, eBay, business sale, demo, damage, etc.)
- Money amount
- Notes
- System should be extensible for additional fields in the future

### Inventory Management
- Track current inventory levels
- Updated by online sales, in-person sales, giveaways, damages, etc.

### Giveaway Management
- Create and schedule weekly giveaways
- Track giveaway history and winners

### Business Expense Tracking
- Log business expenses (supplies, event fees, shipping materials, etc.)
- Track B2B order activity
- Both internal expenses and business-account orders are tracked

### Business Account Management
- Review pending business account applications
- Approve or reject resale certificates
- View all business accounts

### Blog CMS
- Create, edit, publish, and delete blog posts

### Map Management
- Add, edit, and remove retail store locations on the interactive map

---

## Promotions & Marketing

### Referral System
- Infrastructure for referral tracking (unique referral links per user)
- Reward structure: **TBD** (discount codes, store credit, points — to be decided later)

### Discount Codes
- System for creating and managing discount codes
- Types TBD: percentage off, fixed amount, free shipping, or combinations

### Weekly Giveaway
- Automated weekly giveaway (see page description above)
- Prize: TBD (likely a copy of Hidden Marks)

---

## Email System

### Provider
- TBD (SendGrid, Resend, or AWS SES recommended)

### Transactional Emails
- **Style:** Clean and simple (professional, minimal — not heavily branded)
- **Triggers:**
  - Account creation (magic link for sign-in)
  - Order confirmation / receipt (customers)
  - Invoice (business accounts)
  - Business account approved/rejected
  - Giveaway winner notification
  - Help request responses (when offline tickets are answered)

---

## Design & Aesthetic

### Color Palette
- **Primary:** Black, red, white
- Dark theme throughout

### Typography
- Typography-focused design — type is a primary design element
- Distressed / textured typography fits the aesthetic

### Visual Style
- **Futuristic / dystopian / cyberpunk**
- Broken down, rusted, textured surfaces
- Geometric shapes and patterns
- Micrographics (small detailed informational graphics)
- HUD-like elements (thin lines, data readouts, scanline effects)
- Card design motifs woven throughout the site

### Interactivity & Animation
- **Game "juice"** — satisfying micro-interactions, particle effects, screen shakes, smooth transitions
- Floating/rotating 3D cards on the home page
- Interactive elements that make the site feel fun to play with
- Hover effects, scroll animations, parallax
- 3D card viewer with rotation controls

### Assets
- Logo: exists
- Card art (20–50 designs): exists
- Brand guidelines: work in progress, not finalized

---

## Open Questions & TBD Items

These items need decisions before or during implementation:

1. **Retail price** for Hidden Marks
2. **Exact tiered pricing** breakpoints for business accounts
3. **Game rules and mechanics** (needed for interactive tutorial and AI chatbot training)
4. **Referral reward structure** (discount codes, store credit, points, etc.)
5. **Discount code types** to support
6. **Weekly giveaway rules** (one win per account ever? cooldown? what product?)
7. **Easter egg specifics** (what they are, where they're hidden, what rewards if any)
8. **Blog features** (comments, categories/tags, search, social sharing)
9. **Brand guidelines** finalization
10. **Email provider** selection
11. **Database** selection (PostgreSQL recommended)
12. **Hosting provider** (Vercel or Render recommended for Next.js; migrating off Squarespace)
13. **Map provider** (Google Maps vs Mapbox)
14. **AI chatbot** provider/approach for offline chat
15. **Sales tax** calculation approach
16. **MVP phasing** — what to build and launch first vs. later phases

---

## Suggested MVP Phasing

*(Recommendation — to be confirmed)*

### Phase 1 — Storefront MVP
- Home page with product showcase
- Product page with purchase flow (Stripe)
- Customer accounts (magic link auth)
- Order confirmation emails
- Basic responsive layout with the dark/red/white theme
- Contact form

### Phase 2 — Business Operations
- Employee dashboard (orders, inventory, stats)
- In-person sales tracking
- Business accounts (registration, approval, bulk pricing, invoices)
- Business expense tracking

### Phase 3 — Content & Community
- Blog with built-in CMS
- Interactive map
- Interactive tutorial
- Chat bubble (hybrid: live + AI + message form)

### Phase 4 — Engagement & Polish
- Referral system
- Discount codes
- Weekly giveaway
- 3D card viewer
- Floating cards on home page
- Easter eggs and puzzles
- Full animations, juice, and interactive polish
