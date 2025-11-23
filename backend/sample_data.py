# Mock sources and companies used by the backend's multi-source research.
SAMPLE_COMPANIES = {
    "Google": {
        "industry": "Technology",
        "headquarters": "Mountain View, CA",
        "founded": 1998,
        "employees": 156500,
        "notes": "Known for search engine and AI research."
    },
    "Microsoft": {
        "industry": "Technology",
        "headquarters": "Redmond, WA",
        "founded": 1975,
        "employees": 221000,
        "notes": "Focus on software, cloud computing, and AI."
    },
    "Tesla": {
        "industry": "Automotive & Energy",
        "headquarters": "Palo Alto, CA",
        "founded": 2003,
        "employees": 110000,
        "notes": "Electric vehicles and clean energy solutions."
    }
}

# Mock research "sources". These simulate different websites/reports.
MOCK_SOURCES = [
    {
        "name": "CorporateSite",
        "weight": 0.5,
        "data": {
            "Google": {"founded": 1998, "headquarters": "Mountain View, CA"},
            "Microsoft": {"founded": 1975, "headquarters": "Redmond, WA"},
            "Tesla": {"founded": 2003, "headquarters": "Palo Alto, CA"}
        }
    },
    {
        "name": "OldArchive",
        "weight": 0.2,
        "data": {
            # Intentionally add a conflicting founded year for Google
            "Google": {"founded": 1996, "headquarters": "Mountain View, CA"},
            "Microsoft": {"founded": 1975},
            "Tesla": {"founded": 2003}
        }
    },
    {
        "name": "NewsReport",
        "weight": 0.3,
        "data": {
            "Google": {"founded": 1998},
            "Microsoft": {"founded": 1975},
            "Tesla": {"founded": 2003}
        }
    }
]
