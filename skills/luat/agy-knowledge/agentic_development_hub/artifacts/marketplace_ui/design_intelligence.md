# Design Intelligence Standards

Distilled guidelines for building high-quality, agentic AI interfaces.

## UI/UX Pro Max Core Rules
These rules ensure a premium look and feel while maintaining accessibility and performance.

### 1. Visual Quality
- **Antialiasing**: Always apply `antialiased` to the body or main container.
- **Selection**: Customize text selection colors (e.g., `selection:bg-primary/30`) to match brand accents.
- **Iconography**: Use consistent SVG icon sets (Lucide React or HeroIcons). **Never** use emojis as primary UI icons.
- **Glassmorphism**: Use `backdrop-blur-md` with semi-transparent backgrounds (`bg-surface/80`).

### 2. Interaction
- **Touch Targets**: Minimum `44x44px` for all clickable/tappable elements.
- **Cursors**: Explicitly add `cursor-pointer` to cards, buttons, and interactive images.
- **Stability**: Ensure hover effects (like scaling or border changes) do not shift the layout. Use colors or opacity transitions (150-300ms).

### 3. Accessibility
- **Contrast**: Maintain a 4.5:1 ratio for all body text.
- **Focus States**: Visible rings for keyboard navigation.

## Stitch AI UI Prompting
When using AI generators (like Google Stitch) to prototype designs, follow these prompting patterns:

### Structure
1.  **Context**: Define the industry (e.g., "Healthcare SaaS", "AI Skills Marketplace").
2.  **Components**: Explicitly list sections (Header, Hero, Pricing Grid).
3.  **Visual Style**: Specify "Pro Max" keywords (glassmorphic, minimalist, dark mode).
4.  **Layout**: Mention specific layouts (card-based, bento grid, sticky).

### Example
> "Landing page for an AI Skills marketplace. Hero section with violet/cyan gradient text, sticky glassmorphic header, and a responsive grid of card-based products. Use generous white space and professional dark mode aesthetic."
