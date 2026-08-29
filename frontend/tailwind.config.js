/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Design tokens for the "transcript scan" theme.
        ink: {
          950: "#0A0D12", // page background
          900: "#0F141B", // header / input bar
          800: "#151B23", // panels, assistant bubbles
          700: "#1E2630", // borders, dividers
          600: "#2A3441", // hover states
        },
        mist: {
          400: "#5B6B7C", // muted text / placeholders
          300: "#8B98A5", // secondary text
          100: "#E6EDF3", // primary text
        },
        signal: {
          DEFAULT: "#5B8DEF", // primary accent — links, user bubble, focus rings
          dim: "#3B5C99",
        },
        cue: {
          DEFAULT: "#F5A623", // secondary accent — recording/processing cue
          dim: "#8A5E17",
        },
        danger: {
          DEFAULT: "#F0555B",
          dim: "#3A1E20",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      keyframes: {
        scan: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(400%)" },
        },
        blink: {
          "0%, 80%, 100%": { opacity: "0.2" },
          "40%": { opacity: "1" },
        },
      },
      animation: {
        scan: "scan 1.4s ease-in-out infinite",
        blink1: "blink 1.4s infinite ease-in-out both",
        blink2: "blink 1.4s infinite ease-in-out 0.2s both",
        blink3: "blink 1.4s infinite ease-in-out 0.4s both",
      },
    },
  },
  plugins: [],
};
