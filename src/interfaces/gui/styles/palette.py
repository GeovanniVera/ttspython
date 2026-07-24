# Color palettes — exact hex values from design/style-guide.html (section 08 handoff).
# QSS does not support CSS variables; we interpolate with .format() at runtime.

# ── Ink (dark / default) ──────────────────────────────
DARK_PALETTE = {
    # Surfaces
    "bg_base":      "#12141A",
    "bg_panel":     "#1A1D26",
    "bg_card":      "#242835",
    # Borders
    "border":       "#333849",
    "border_soft":  "#454C61",
    # Radii
    "radius_md":    "10px",
    # Text
    "text_primary":  "#ECEAE4",
    "text_secondary":"#9498A3",
    # Accents — identity
    "copper":        "#E2925B",
    "copper_hover":  "#EFAD82",
    "copper_dark":   "#C97740",
    "teal":          "#4FA8A0",
    "teal_dark":     "#3D8C85",
    # Accents — signal
    "signal_green":       "#3FAE6A",
    "signal_green_hover": "#4CC17C",
    "signal_red":         "#C4453A",
    "signal_red_hover":   "#D65B4F",
    "signal_amber":       "#D98A3D",
    "signal_amber_hover": "#E6A15C",
}

# ── Paper (light) ─────────────────────────────────────
LIGHT_PALETTE = {
    # Surfaces
    "bg_base":      "#F6F3EC",
    "bg_panel":     "#EDE8DD",
    "bg_card":      "#FFFFFF",
    # Borders
    "border":       "#DDD6C5",
    "border_soft":  "#C9C1AC",
    # Radii
    "radius_md":    "10px",
    # Text
    "text_primary":  "#211E19",
    "text_secondary":"#7A7364",
    # Accents — identity (same across modes)
    "copper":        "#E2925B",
    "copper_hover":  "#EFAD82",
    "copper_dark":   "#C97740",
    "teal":          "#4FA8A0",
    "teal_dark":     "#3D8C85",
    # Accents — signal (same across modes)
    "signal_green":       "#3FAE6A",
    "signal_green_hover": "#4CC17C",
    "signal_red":         "#C4453A",
    "signal_red_hover":   "#D65B4F",
    "signal_amber":       "#D98A3D",
    "signal_amber_hover": "#E6A15C",
}
