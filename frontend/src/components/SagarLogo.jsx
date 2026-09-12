import React from "react";

export default function SagarLogo({ size = 24, className = "", style = {} }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 36 36"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`sagar-logo-svg ${className}`}
      style={{ display: "inline-block", verticalAlign: "middle", flexShrink: 0, ...style }}
    >
      <defs>
        {/* Modern Ocean & Tech Linear Gradients */}
        <linearGradient id="sagarHullGrad" x1="6" y1="8" x2="30" y2="28" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#38bdf8" />
          <stop offset="50%" stopColor="#0284c7" />
          <stop offset="100%" stopColor="#0f766e" />
        </linearGradient>

        <linearGradient id="sagarDeckGrad" x1="12" y1="4" x2="24" y2="16" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#ffffff" />
          <stop offset="100%" stopColor="#e0f2fe" />
        </linearGradient>

        <linearGradient id="sagarWaveGrad1" x1="4" y1="26" x2="32" y2="26" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#38bdf8" />
          <stop offset="50%" stopColor="#06b6d4" />
          <stop offset="100%" stopColor="#2dd4bf" />
        </linearGradient>

        <linearGradient id="sagarWaveGrad2" x1="7" y1="31" x2="29" y2="31" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#0284c7" />
          <stop offset="100%" stopColor="#0d9488" />
        </linearGradient>
      </defs>

      {/* AI Radar / Beacon Diamond at Mast Apex */}
      <polygon
        points="18,2.5 20.8,6.2 18,9.5 15.2,6.2"
        fill="#38bdf8"
      />

      {/* Navigation Mast / Central Signal Beam */}
      <line
        x1="18"
        y1="9.5"
        x2="18"
        y2="14"
        stroke="#ffffff"
        strokeWidth="1.8"
        strokeLinecap="round"
      />

      {/* Bridge / Wheelhouse Superstructure */}
      <path
        d="M13.5 13.5H22.5L21.2 17H14.8L13.5 13.5Z"
        fill="url(#sagarDeckGrad)"
        stroke="#0284c7"
        strokeWidth="0.8"
      />

      {/* Modern Faceted Ship Hull */}
      <path
        d="M6.5 17.5L18 26.5L29.5 17.5L26.5 22L18 28.5L9.5 22L6.5 17.5Z"
        fill="url(#sagarHullGrad)"
      />

      {/* Center Hull Keel Accent Line */}
      <path
        d="M18 17.5V28.5"
        stroke="#ffffff"
        strokeWidth="1.2"
        strokeOpacity="0.75"
        strokeLinecap="round"
      />

      {/* Dynamic Ocean Hydro-Wave 1 (Upper Wave) */}
      <path
        d="M4.5 26.5C8.5 23.5 13.5 28.5 18 26.5C22.5 24.5 27.5 29.5 31.5 26.5"
        stroke="url(#sagarWaveGrad1)"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Dynamic Ocean Hydro-Wave 2 (Lower Wave) */}
      <path
        d="M7 31C10.5 28.5 14.5 32.5 18 31C21.5 29.5 25.5 33.5 29 31"
        stroke="url(#sagarWaveGrad2)"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity="0.85"
      />
    </svg>
  );
}
