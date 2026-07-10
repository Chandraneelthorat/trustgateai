import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        gate: {
          900: "#0b1224",
          700: "#1c2f5b",
          500: "#2f81f7",
          300: "#9cc5ff",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
