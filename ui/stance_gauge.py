"""
Visual stance gauge for displaying hawkish/dovish score in an accessible way.
"""
import streamlit as st


def render_stance_gauge(score: float, label: str):
    """
    Renders a color-coded, emoji-labelled stance gauge.
    Score is typically in [-3, +3]. Positive = hawkish, Negative = dovish.
    """
    # Normalized to 0–100 for the progress bar
    normalized = min(max((score + 3) / 6, 0), 1)

    if label == "hawkish":
        color = "#e05252"
        emoji = "🦅"
        plain = "Leaning toward higher rates"
    elif label == "dovish":
        color = "#5285e0"
        emoji = "🕊️"
        plain = "Leaning toward cutting rates"
    else:
        color = "#52b052"
        emoji = "⚖️"
        plain = "Watching and waiting — no strong lean"

    st.markdown(
        f"""
        <style>
        .gauge-container {{
            background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
            border: 1px solid {color}44;
            border-radius: 16px;
            padding: 1.2rem 1.6rem;
            margin-bottom: 1rem;
        }}
        .gauge-label {{
            font-size: 1.15rem;
            font-weight: 700;
            color: {color};
        }}
        .gauge-plain {{
            font-size: 0.88rem;
            color: #c9d1e0;
            margin-top: 0.2rem;
            margin-bottom: 0.8rem;
        }}
        .gauge-bar-bg {{
            background: #2d3561;
            border-radius: 999px;
            height: 10px;
            position: relative;
        }}
        .gauge-bar-fill {{
            background: {color};
            border-radius: 999px;
            height: 10px;
            width: {normalized * 100:.1f}%;
            transition: width 0.5s ease;
        }}
        .gauge-axis {{
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: #8893a8;
            margin-top: 0.3rem;
        }}
        </style>
        <div class="gauge-container">
            <div class="gauge-label">{emoji} {label.capitalize()} — Score: {score:+.2f}</div>
            <div class="gauge-plain">{plain}</div>
            <div class="gauge-bar-bg">
                <div class="gauge-bar-fill"></div>
            </div>
            <div class="gauge-axis">
                <span>🕊️ Very Dovish</span>
                <span>Neutral</span>
                <span>Hawkish 🦅</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
