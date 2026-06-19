# Design Document: Macro Modern Prototype

## 1. Project Overview
Macro is a "free Plex alternative" focused on self-hosting media. The goal of this prototype is to transform the existing basic UI into a high-fidelity, modern web experience that showcases the project's potential.

## 2. Visual Identity
- **Aesthetic**: Dark Mode by default, utilizing "Glassmorphism" (background blurs, semi-transparent surfaces) and **Scutoid-inspired geometric patterns**.
- **Color Palette**:
  - Background: Deep Charcoals/Blacks (#0a0a0a)
  - Primary Accent: Electric Purple/Blue gradient (#7b2ff7 -> #2196f3)
  - Text: High-contrast Whites and muted Silvers.
- **Typography**: Modern Sans-serif (Inter or Roboto, to match previous standards).

## 3. Key Features & Views
### A. Landing Page
- **Hero Section**: Impactful headline with a "Get Started" call-to-action.
- **Feature Grid**: Visually rich cards for "Music", "Video", "Photos", and "Cloud Storage" using **Material-style iconography**.
- **Interactive Price Section**: A playful section highlighting the "$0" price tag, cycling through values like "Free", "0 BTC", and "There is no price" (following the original scutoid site logic).

### B. Authentication
- Minimalist login form centered on a blurred background.
- Smooth transitions into the dashboard.

### C. Media Dashboard
- **Sidebar**: Elegant navigation for Categories (Music, Video, Files).
- **Media Grid**: Responsive grid of media cards with hover effects.
- **Global Player**: A persistent bottom bar for music playback with waveform/progress visualization.

## 4. Technical Stack
- **Framework**: React (TypeScript)
- **Styling**: Vanilla CSS (using modern features like CSS Variables, Flexbox, and Grid).
- **Icons**: Lucide-React or simple SVG paths.
- **Interactions**: CSS Transitions for smooth hovers and state changes.

## 5. Implementation Strategy
1. **Mock Data**: Create a robust set of mock media items to ensure the UI feels "alive" and full.
2. **Component Architecture**: Build reusable components for `Button`, `Card`, `Sidebar`, and `MediaGrid`.
3. **Responsive Design**: Ensure the prototype looks excellent on both Desktop and Mobile.
4. **Interactive Demo**: Implement functional navigation between landing, login, and dashboard states.

## 6. Delivery
The prototype will be delivered as a directory containing the source code and a way to preview it (e.g., a single-file build or a simple dev server setup).
