import React from 'react';
import {
  Trophy,
  Swords,
  Brain,
  Flame,
  Zap,
  Target,
  Sparkles,
  Snowflake,
  Waves,
  Compass,
  Gamepad2,
  Medal,
  Award,
  Globe2,
} from 'lucide-react';

export const CATEGORY_CONFIG = {
  "Field & Team Ball Sports": {
    icon: Trophy,
    color: "emerald",
    bg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    badge: "bg-emerald-500 text-slate-950",
    ring: "focus:ring-emerald-500",
  },
  "Combat Sports & Martial Arts": {
    icon: Swords,
    color: "red",
    bg: "bg-red-500/10 text-red-400 border-red-500/30",
    badge: "bg-red-500 text-white",
    ring: "focus:ring-red-500",
  },
  "Board, Tile & Strategy Games": {
    icon: Brain,
    color: "purple",
    bg: "bg-purple-500/10 text-purple-400 border-purple-500/30",
    badge: "bg-purple-500 text-white",
    ring: "focus:ring-purple-500",
  },
  "Indigenous, Folk & Traditional Games": {
    icon: Flame,
    color: "amber",
    bg: "bg-amber-500/10 text-amber-400 border-amber-500/30",
    badge: "bg-amber-500 text-slate-950",
    ring: "focus:ring-amber-500",
  },
  "Racquet & Paddle Sports": {
    icon: Zap,
    color: "cyan",
    bg: "bg-cyan-500/10 text-cyan-400 border-cyan-500/30",
    badge: "bg-cyan-500 text-slate-950",
    ring: "focus:ring-cyan-500",
  },
  "Target & Precision Sports": {
    icon: Target,
    color: "yellow",
    bg: "bg-yellow-500/10 text-yellow-400 border-yellow-500/30",
    badge: "bg-yellow-500 text-slate-950",
    ring: "focus:ring-yellow-500",
  },
  "Mind Sports & Tabletop Games": {
    icon: Sparkles,
    color: "indigo",
    bg: "bg-indigo-500/10 text-indigo-400 border-indigo-500/30",
    badge: "bg-indigo-500 text-white",
    ring: "focus:ring-indigo-500",
  },
  "Winter & Ice Sports": {
    icon: Snowflake,
    color: "sky",
    bg: "bg-sky-500/10 text-sky-400 border-sky-500/30",
    badge: "bg-sky-500 text-slate-950",
    ring: "focus:ring-sky-500",
  },
  "Water & Aquatic Sports": {
    icon: Waves,
    color: "blue",
    bg: "bg-blue-500/10 text-blue-400 border-blue-500/30",
    badge: "bg-blue-500 text-white",
    ring: "focus:ring-blue-500",
  },
  "Extreme & Adventure Sports": {
    icon: Compass,
    color: "orange",
    bg: "bg-orange-500/10 text-orange-400 border-orange-500/30",
    badge: "bg-orange-500 text-slate-950",
    ring: "focus:ring-orange-500",
  },
  "Esports & Competitive Digital Gaming": {
    icon: Gamepad2,
    color: "pink",
    bg: "bg-pink-500/10 text-pink-400 border-pink-500/30",
    badge: "bg-pink-500 text-white",
    ring: "focus:ring-pink-500",
  },
  "Athletic & Gymnastic Disciplines": {
    icon: Medal,
    color: "teal",
    bg: "bg-teal-500/10 text-teal-400 border-teal-500/30",
    badge: "bg-teal-500 text-slate-950",
    ring: "focus:ring-teal-500",
  },
};

export const getCategoryConfig = (category) => {
  return CATEGORY_CONFIG[category] || {
    icon: Trophy,
    color: "emerald",
    bg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    badge: "bg-emerald-500 text-slate-950",
  };
};

export const REGIONS = [
  "All",
  "East Asia",
  "South Asia",
  "Southeast Asia",
  "Central & West Asia",
  "Europe",
  "Sub-Saharan Africa",
  "North America",
  "Latin America & Caribbean",
  "Oceania & Pacific",
  "Global & Multi-Regional",
];
