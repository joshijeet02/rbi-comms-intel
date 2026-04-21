RBI_SOURCES = [
    {
        "series_key": "mpc-minutes",
        "document_type": "MPC Minutes",
        "index_url": "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx",
        "base_url": "https://www.rbi.org.in",
        "match_terms": ("minutes of the monetary policy committee",),
    },
    {
        "series_key": "mpc-statement",
        "document_type": "Monetary Policy Statement",
        "index_url": "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=all",
        "base_url": "https://www.rbi.org.in",
        "match_terms": (
            "resolution of the monetary policy committee",
            "monetary policy statement",
            "monetary policy",
        ),
    },
    {
        "series_key": "governor-speech",
        "document_type": "Governor Speech",
        "index_url": "https://www.rbi.org.in/Scripts/BS_SpeechesView.aspx",
        "base_url": "https://www.rbi.org.in",
        "match_terms": ("speech", "address"),
    },
    {
        "series_key": "deputy-governor-speech",
        "document_type": "Deputy Governor Speech",
        "index_url": "https://www.rbi.org.in/Scripts/BS_SpeechesView.aspx",
        "base_url": "https://www.rbi.org.in",
        "match_terms": ("deputy governor", "speech"),
    },
    {
        "series_key": "mpr",
        "document_type": "Monetary Policy Report",
        "index_url": "https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=950",
        "base_url": "https://www.rbi.org.in",
        "match_terms": ("monetary policy report",),
    },
    {
        "series_key": "annual-report",
        "document_type": "RBI Annual Report",
        "index_url": "https://www.rbi.org.in/Scripts/AnnualReportMainDisplay.aspx",
        "base_url": "https://www.rbi.org.in",
        "match_terms": ("annual report",),
    },
]
