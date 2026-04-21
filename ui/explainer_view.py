"""
Layman-friendly glossary and explainer for RBI concepts.
"""
import streamlit as st


GLOSSARY = {
    "Repo Rate": (
        "💰",
        "The interest rate at which the RBI lends money to commercial banks. "
        "When this goes up, banks pass the cost on to you — your home loan and car loan EMIs rise.",
    ),
    "Hawkish": (
        "🦅",
        "When the RBI is 'hawkish', it is worried about prices rising too fast (inflation). "
        "This usually means interest rates will go up or stay high to slow down spending.",
    ),
    "Dovish": (
        "🕊️",
        "When the RBI is 'dovish', it wants to boost growth and jobs. "
        "This usually means interest rates may fall, making loans cheaper.",
    ),
    "Inflation": (
        "📈",
        "How fast prices are rising across the economy. The RBI tries to keep inflation "
        "near 4%. When inflation is too high, your household budget gets squeezed.",
    ),
    "MPC (Monetary Policy Committee)": (
        "🏛️",
        "A group of 6 people — 3 from the RBI, 3 independent experts — who vote every "
        "two months on whether to change interest rates.",
    ),
    "Basis Points (bps)": (
        "📐",
        "A unit for measuring tiny changes in interest rates. "
        "1 basis point = 0.01%. So '25 bps' means a rate moved by 0.25%.",
    ),
    "Liquidity": (
        "💧",
        "How much cash is flowing freely in the banking system. "
        "Tight liquidity means banks have less money to lend; easy liquidity means more.",
    ),
    "GDP Growth": (
        "📊",
        "How fast the entire Indian economy is expanding. Higher GDP growth generally "
        "means more jobs and better incomes across the country.",
    ),
    "Stance": (
        "🧭",
        "The RBI's overall attitude toward the economy right now. "
        "'Withdrawal of accommodation' means moving away from easy money. 'Neutral' means watching and waiting.",
    ),
    "Transmission": (
        "⚡",
        "How quickly an RBI rate change actually reaches your bank's lending rates. "
        "If transmission is slow, a rate cut may take months before your EMI falls.",
    ),
}


def render_explainer_view():
    st.subheader("📖 RBI Jargon, Decoded")
    st.caption(
        "New to central bank speak? This glossary translates key RBI terms into plain English."
    )

    st.markdown(
        """
        <style>
        .glossary-card {
            background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
            border: 1px solid #2d3561;
            border-radius: 12px;
            padding: 1.1rem 1.4rem;
            margin-bottom: 0.8rem;
        }
        .glossary-term {
            font-size: 1.05rem;
            font-weight: 700;
            color: #7eb8f7;
            margin-bottom: 0.3rem;
        }
        .glossary-def {
            font-size: 0.92rem;
            color: #c9d1e0;
            line-height: 1.55;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    search = st.text_input("🔍 Filter terms", placeholder="e.g. inflation, EMI, rate...")

    cols = st.columns(2)
    entries = [
        (term, icon, defn)
        for term, (icon, defn) in GLOSSARY.items()
        if not search or search.lower() in term.lower() or search.lower() in defn.lower()
    ]

    for i, (term, icon, defn) in enumerate(entries):
        with cols[i % 2]:
            st.markdown(
                f"""
                <div class="glossary-card">
                    <div class="glossary-term">{icon} {term}</div>
                    <div class="glossary-def">{defn}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown("### 🤔 How does the RBI actually affect me?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(
            "**Home Loan EMIs** 🏠\n\n"
            "When the repo rate goes up by 0.25%, your EMI on a ₹50L home loan rises roughly ₹750–₹900/month."
        )
    with col2:
        st.info(
            "**Fixed Deposits** 🏦\n\n"
            "A hawkish RBI is good for savers — banks tend to offer higher FD rates when borrowing costs rise."
        )
    with col3:
        st.info(
            "**Your Grocery Bill** 🛒\n\n"
            "The RBI watches food prices closely. High inflation erodes your purchasing power — the same income buys less."
        )
