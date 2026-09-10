import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup


# ============================================================
# CONFIG
# ============================================================

PORT_SCHEDULE_URLS = {
    "Dhamra":
        "https://www.adaniports.com/ports-and-terminals/dhamra-port/vesselschedule",

    "Gangavaram":
        "https://www.adaniports.com/ports-and-terminals/gangavaram-port/vesselschedule",
}

HISTORY_FILE = "data/port_congestion_history.csv"


# ============================================================
# DIRECTORY
# ============================================================

os.makedirs("data", exist_ok=True)


# ============================================================
# FETCH PAGE
# ============================================================

def _get_schedule_html(port_name):

    url = PORT_SCHEDULE_URLS.get(port_name)

    if not url:
        raise ValueError(
            f"Unsupported port: {port_name}"
        )

    response = requests.get(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0 Safari/537.36"
            ),
            "Accept":
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language":
                "en-US,en;q=0.9",
        },
        timeout=30
    )

    response.raise_for_status()

    return response.text


# ============================================================
# CLEAN TEXT
# ============================================================

def _clean_text(text):

    return " ".join(
        text.replace("\xa0", " ").split()
    )


# ============================================================
# COUNT ROWS FROM TABLES
# ============================================================

def _count_table_rows(soup, section_name):

    count = 0

    for table in soup.find_all("table"):

        table_text = _clean_text(
            table.get_text(
                " ",
                strip=True
            )
        )

        if section_name.lower() not in table_text.lower():
            continue

        rows = table.find_all("tr")

        for row in rows:

            row_text = _clean_text(
                row.get_text(
                    " ",
                    strip=True
                )
            )

            if not row_text:
                continue

            upper = row_text.upper()

            # Ignore headings
            if "VESSEL NAME" in upper:
                continue

            if "VESSELS AT BERTH" in upper:
                continue

            if "VESSELS AT ANCHORAGE" in upper:
                continue

            if "VACANT" in upper:
                continue

            # Require some vessel-like content
            cells = row.find_all(
                ["td", "th"]
            )

            if len(cells) >= 2:
                count += 1

    return count


# ============================================================
# TEXT-BASED FALLBACK
# ============================================================

def _count_from_text(soup, section_name, next_sections):

    text = soup.get_text(
        " ",
        strip=True
    )

    text = _clean_text(text)

    pattern = re.escape(section_name)

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    if not match:
        return 0

    remaining = text[
        match.end():
    ]

    # Find next major section
    positions = []

    for section in next_sections:

        found = re.search(
            re.escape(section),
            remaining,
            flags=re.IGNORECASE
        )

        if found:
            positions.append(
                found.start()
            )

    if positions:

        remaining = remaining[
            :min(positions)
        ]

    # --------------------------------------------------------
    # Try to identify vessel rows.
    #
    # This fallback is intentionally conservative.
    # --------------------------------------------------------

    lines = re.split(
        r"\n+",
        remaining
    )

    count = 0

    for line in lines:

        line = _clean_text(line)

        if not line:
            continue

        upper = line.upper()

        if "VESSEL NAME" in upper:
            continue

        if "VACANT" in upper:
            continue

        if len(line) < 4:
            continue

        count += 1

    return count


# ============================================================
# EXTRACT VESSEL COUNTS
# ============================================================

def _extract_vessel_counts(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # --------------------------------------------------------
    # First attempt: actual HTML tables
    # --------------------------------------------------------

    berthed = _count_table_rows(
        soup,
        "Vessels at Berth"
    )

    anchorage = _count_table_rows(
        soup,
        "Vessels at Anchorage"
    )

    # --------------------------------------------------------
    # Fallback: rendered text
    # --------------------------------------------------------

    if berthed == 0:

        berthed = _count_from_text(
            soup,
            "Vessels at Berth",
            [
                "Vessels at Anchorage",
                "Expected Vessels",
                "Vessels Sailed",
            ]
        )

    if anchorage == 0:

        anchorage = _count_from_text(
            soup,
            "Vessels at Anchorage",
            [
                "Expected Vessels",
                "Vessels Sailed",
                "Vessels at Berth",
            ]
        )

    return (
        int(berthed),
        int(anchorage)
    )


# ============================================================
# CONGESTION SCORE
# ============================================================

def _calculate_score(
    berthed,
    anchorage
):

    total = (
        berthed +
        anchorage
    )

    if total == 0:
        return 0.0

    return round(
        (anchorage / total) * 100,
        2
    )


# ============================================================
# CONGESTION LEVEL
# ============================================================

def _get_level(score):

    if score < 10:
        return "Low"

    if score < 25:
        return "Moderate"

    if score < 40:
        return "High"

    return "Severe"


# ============================================================
# SAVE DAILY OBSERVATION
# ============================================================

def _save_observation(
    port_name,
    berthed,
    anchorage,
    score
):

    today = pd.Timestamp.now().normalize()

    new_row = pd.DataFrame([
        {
            "date": today,
            "port": port_name,
            "berthed_vessels": berthed,
            "waiting_vessels": anchorage,
            "congestion_score": score,
        }
    ])

    # --------------------------------------------------------
    # Read existing history
    # --------------------------------------------------------

    if os.path.exists(HISTORY_FILE):

        try:

            history = pd.read_csv(
                HISTORY_FILE
            )

            if history.empty:

                history = pd.DataFrame(
                    columns=[
                        "date",
                        "port",
                        "berthed_vessels",
                        "waiting_vessels",
                        "congestion_score",
                    ]
                )

        except (
            pd.errors.EmptyDataError,
            pd.errors.ParserError
        ):

            history = pd.DataFrame(
                columns=[
                    "date",
                    "port",
                    "berthed_vessels",
                    "waiting_vessels",
                    "congestion_score",
                ]
            )

    else:

        history = pd.DataFrame(
            columns=[
                "date",
                "port",
                "berthed_vessels",
                "waiting_vessels",
                "congestion_score",
            ]
        )

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    history = pd.concat(
        [
            history,
            new_row
        ],
        ignore_index=True
    )

    history["date"] = pd.to_datetime(
        history["date"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # One observation per port per day
    # --------------------------------------------------------

    history = (
        history
        .dropna(subset=["date"])
        .sort_values("date")
        .drop_duplicates(
            subset=[
                "date",
                "port"
            ],
            keep="last"
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    history.to_csv(
        HISTORY_FILE,
        index=False
    )

    return history


# ============================================================
# MAIN PROVIDER
# ============================================================

def get_port_congestion(
    port_name
):

    if port_name not in PORT_SCHEDULE_URLS:

        return {
            "available": False,
            "port": port_name,
            "score": None,
            "level": "Unavailable",
            "berthed_vessels": None,
            "waiting_vessels": None,
            "source": None,
        }

    try:

        print(
            f"\nFetching {port_name}..."
        )

        html = _get_schedule_html(
            port_name
        )

        print(
            f"HTML received: {len(html)} characters"
        )

        berthed, anchorage = (
            _extract_vessel_counts(
                html
            )
        )

        print(
            f"Berth: {berthed} | "
            f"Anchorage: {anchorage}"
        )

        score = _calculate_score(
            berthed,
            anchorage
        )

        level = _get_level(
            score
        )

        # ----------------------------------------------------
        # SAVE TO HISTORY
        # ----------------------------------------------------

        _save_observation(
            port_name,
            berthed,
            anchorage,
            score
        )

        return {
            "available": True,
            "port": port_name,
            "score": score,
            "level": level,
            "berthed_vessels": berthed,
            "waiting_vessels": anchorage,
            "source":
                PORT_SCHEDULE_URLS[
                    port_name
                ],
        }

    except Exception as error:

        return {
            "available": False,
            "port": port_name,
            "score": None,
            "level": "Unavailable",
            "berthed_vessels": None,
            "waiting_vessels": None,
            "source":
                PORT_SCHEDULE_URLS.get(
                    port_name
                ),
            "error": str(error),
        }


# ============================================================
# READ HISTORY
# ============================================================

def get_port_congestion_history(
    port_name=None
):

    if not os.path.exists(
        HISTORY_FILE
    ):

        return pd.DataFrame(
            columns=[
                "date",
                "port",
                "berthed_vessels",
                "waiting_vessels",
                "congestion_score",
            ]
        )

    try:

        history = pd.read_csv(
            HISTORY_FILE
        )

    except pd.errors.EmptyDataError:

        return pd.DataFrame(
            columns=[
                "date",
                "port",
                "berthed_vessels",
                "waiting_vessels",
                "congestion_score",
            ]
        )

    history["date"] = pd.to_datetime(
        history["date"],
        errors="coerce"
    )

    if port_name:

        history = history[
            history["port"] == port_name
        ]

    return (
        history
        .sort_values("date")
        .reset_index(drop=True)
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PORT CONGESTION PROVIDER TEST")
    print("=" * 60)

    for port in [
        "Dhamra",
        "Gangavaram"
    ]:

        result = get_port_congestion(
            port
        )

        print(
            "\nRESULT:"
        )

        print(result)

    print(
        "\n" + "=" * 60
    )

    print(
        "HISTORICAL CSV:"
    )

    print(
        HISTORY_FILE
    )

    history = get_port_congestion_history()

    print(
        history.to_string(
            index=False
        )
    )

    print(
        "\nTotal rows:",
        len(history)
    )