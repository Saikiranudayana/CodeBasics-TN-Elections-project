"""utils/constants.py — Shared constants for TN Election Dashboard."""

PARTY_COLORS = {
    "DMK":     "#E31E24",   # red
    "AIADMK":  "#00853F",   # green
    "TVK":     "#FF6B00",   # orange (new party 2026)
    "INC":     "#007DC6",   # congress blue
    "BJP":     "#FF9933",   # saffron
    "PMK":     "#008080",   # teal
    "VCK":     "#800080",   # purple
    "NTK":     "#D4AF37",   # gold
    "CPI":     "#CC0000",   # dark red
    "CPI(M)":  "#990000",   # darker red
    "NOTA":    "#999999",   # grey
    "IND":     "#AAAAAA",   # light grey
    "AMMK":    "#6B8E23",   # olive
    "DMDK":    "#4169E1",   # royal blue
    "OTHER":   "#CCCCCC",   # fallback
}

REGION_ORDER = ["Chennai Metro", "North", "Central", "Kongu", "Delta", "South"]

MAJOR_PARTIES_2021 = ["DMK", "AIADMK", "INC", "BJP", "PMK", "VCK", "NTK", "NOTA"]
MAJOR_PARTIES_2026 = ["DMK", "AIADMK", "TVK", "INC", "BJP", "PMK", "VCK", "NTK", "NOTA"]

RESERVED_ORDER = ["GEN", "SC", "ST"]

ALLIANCE_2021 = {
    "DMK Alliance": ["DMK", "INC", "CPI", "CPI(M)", "VCK"],
    "AIADMK Alliance": ["AIADMK", "BJP", "PMK"],
    "Third Front": ["NTK", "AMMK", "DMDK"],
}

ALLIANCE_2026 = {
    "TVK Alliance": ["TVK"],
    "DMK Alliance": ["DMK", "INC", "CPI", "CPI(M)", "VCK", "IUML"],
    "AIADMK Alliance": ["AIADMK", "PMK", "BJP", "AMMK"],
    "Others": ["NTK", "DMDK"],
}

TOTAL_SEATS = 234
MAJORITY_MARK = 118
