# Skills Marketplace Implementation Guide

This guide details the pattern for building a premium landing page to showcase and sell AI skills.

## Core Stack
- **Framework**: React + Vite
- **Styling**: Tailwind CSS (Deep Space Theme)
- **Icons**: Lucide React
- **Animation**: Framer Motion

## Rapid Initialization
1.  **Project Creation**:
    ```bash
    npm create-vite@latest skills-landing-page -- --template react
    cd skills-landing-page
    npm install -D tailwindcss postcss autoprefixer
    npm install lucide-react framer-motion
    ```
2.  **Manual Config (Fail-safe for npx failure)**:
    - **`postcss.config.js`**:
    ```javascript
    export default { plugins: { tailwindcss: {}, autoprefixer: {}, }, }
    ```
    - **`tailwind.config.js`**:
    ```javascript
    export default {
      content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
      theme: {
        extend: {
          colors: {
            background: '#0a0a0a',
            surface: '#121212',
            primary: '#8b5cf6', // Violet
            secondary: '#06b6d4', // Cyan
          },
        },
      },
      plugins: [],
    }
    ```

## Component Patterns

### 1. Glassmorphic Sticky Header
Uses scroll detection to trigger background blur and border.
```javascript
export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const handleScroll = () => { setScrolled(window.scrollY > 20); };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled ? 'bg-background/80 backdrop-blur-md border-b border-gray-800' : 'bg-transparent'
    }`}>
      {/* Navigation Content */}
    </header>
  );
}
```

### 2. Animated Hero Section
Uses `framer-motion` for staggered entry animations.
```javascript
<motion.h1
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5, delay: 0.1 }}
  className="..."
>
  Unlock Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">Agentic Potential</span>
</motion.h1>
```

### 3. Skill Card Grid
Uses `group` hover states for interactive arrows and transitions.
```javascript
export default function SkillCard({ skill, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className="group relative rounded-2xl border border-gray-800 bg-surface p-6 hover:border-primary/50"
    >
      <div className="absolute top-0 right-0 p-4 opacity-0 transition-opacity group-hover:opacity-100">
        <ArrowRight className="h-5 w-5 text-primary -rotate-45" />
      </div>
      {/* Card Body */}
    </motion.div>
  );
}
```

## Best Practices
- **Data Decoupling**: Store skill metadata in `src/data/skills.js` to separate content from UI logic.
- **Micro-interactions**: Use 150-300ms transitions for all hover states.
- **Accessibility**: Ensure a 4.5:1 contrast ratio, especially in glassmorphic/transparent layers.
