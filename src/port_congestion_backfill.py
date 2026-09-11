import re
import os
from io import BytesIO

import requests
import pandas as pd
from pypdf import PdfReader


# ============================================================
# CONFIGURATION
# ============================================================

TRAFFIC_URL = "https://paradipport.gov.in/traffic/"

OUTPUT_FILE = "data/port_congestion_history.csv"

START_DATE = pd.Timestamp("2026-06-18")
END_DATE = pd.Timestamp("2026-09-09")

PORT_NAME = "Paradip"


# ============================================================
# 1. GET DAILY TRAFFIC REPORT LINKS
# ============================================================

def get_report_links():

    print("\nFetching Paradip traffic reports...")

    response = requests.get(
        TRAFFIC_URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    html = response.text

    # Example:
    # /uploads/2026/09/dtr0909.pdf

    pattern = re.compile(
        r'href=["\']([^"\']*dtr[^"\']*\.pdf)["\']',
        re.IGNORECASE
    )

    links = pattern.findall(html)

    reports = []

    for link in links:

        if link.startswith("/"):
            url = "https://paradipport.gov.in" + link

        elif link.startswith("http"):
            url = link

        else:
            url = "https://paradipport.gov.in/" + link

        url = url.replace("\\", "/")

        match = re.search(
            r"/uploads/(\d{4})/(\d{2})/dtr(\d{2})(\d{2})\.pdf",
            url,
            re.IGNORECASE
        )

        if not match:
            continue

        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))

        try:
            date = pd.Timestamp(
                year=year,
                month=month,
                day=day
            )
        except Exception:
            continue

        if START_DATE <= date <= END_DATE:

            reports.append({
                "date": date,
                "url": url
            })

    # Remove duplicate dates

    unique_reports = {}

    for report in reports:

        key = report["date"].strftime("%Y-%m-%d")

        unique_reports[key] = report

    reports = list(unique_reports.values())

    reports.sort(
        key=lambda x: x["date"]
    )

    print(
        f"Found {len(reports)} reports."
    )

    if reports:

        print(
            f"Date range: "
            f"{reports[0]['date'].strftime('%Y-%m-%d')} "
            f"-> "
            f"{reports[-1]['date'].strftime('%Y-%m-%d')}"
        )

    return reports


# ============================================================
# 2. DOWNLOAD PDF
# ============================================================

def download_pdf(url):

    response = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    return response.content


# ============================================================
# 3. EXTRACT PDF PAGES
# ============================================================

def extract_pdf_pages(pdf_bytes):

    reader = PdfReader(
        BytesIO(pdf_bytes)
    )

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        try:

            # Layout mode is important because the
            # Paradip report is a table-heavy PDF.

            text = page.extract_text(
                extraction_mode="layout"
            ) or ""

        except TypeError:

            # Fallback for older pypdf versions

            text = page.extract_text() or ""

        except Exception as e:

            print(
                f"WARNING: PDF page "
                f"{page_number} extraction failed: {e}"
            )

            text = ""

        pages.append({
            "page_number": page_number,
            "text": text
        })

    return pages


# ============================================================
# 4. NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    # Non-breaking space
    text = text.replace(
        "\xa0",
        " "
    )

    # Unicode spaces
    text = re.sub(
        r"[\u2000-\u200B\u202F]",
        " ",
        text
    )

    # Windows line endings
    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    return text


# ============================================================
# 5. NORMALIZE VESSEL PREFIX
# ============================================================

def normalize_vessel_prefix(line):

    """
    Converts PDF variations:

        MV.
        M V.
        M V .
        MT.
        M T.
        M T .

    into:

        MV.
        MT.
    """

    line = re.sub(
        r"\bM\s*V\s*\.",
        "MV.",
        line,
        flags=re.IGNORECASE
    )

    line = re.sub(
        r"\bM\s*T\s*\.",
        "MT.",
        line,
        flags=re.IGNORECASE
    )

    line = re.sub(
        r"\bM\s*V\b",
        "MV",
        line,
        flags=re.IGNORECASE
    )

    line = re.sub(
        r"\bM\s*T\b",
        "MT",
        line,
        flags=re.IGNORECASE
    )

    return line


# ============================================================
# 6. BUILD COMPLETE PDF TEXT
# ============================================================

def get_full_text(pages):

    text = ""

    for page in pages:

        text += "\n"

        text += page["text"]

    return normalize_text(text)


# ============================================================
# 7. GET WAITING SECTION
# ============================================================

def get_waiting_section(pages):

    full_text = get_full_text(
        pages
    )

    # Section B starts here.

    start_patterns = [

        r"B\.\s*VESSELS\s+WAITING\s+AT\s+ANCHORAGE",

        r"B\.\s*VESSELS\s+WAITING\s+AT\s+ANCHOR",

        r"VESSELS\s+WAITING\s+AT\s+ANCHORAGE"
    ]

    start_match = None

    for pattern in start_patterns:

        match = re.search(
            pattern,
            full_text,
            flags=re.IGNORECASE
        )

        if match:

            start_match = match

            break

    if start_match is None:

        print(
            "WARNING: Section B not found."
        )

        return ""

    remaining = full_text[
        start_match.end():
    ]

    # Section C starts after waiting vessels.

    end_patterns = [

        r"C\.\s*EXPECTED\s+VESS+EL",

        r"EXPECTED\s+VESS+EL"
    ]

    end_match = None

    for pattern in end_patterns:

        match = re.search(
            pattern,
            remaining,
            flags=re.IGNORECASE
        )

        if match:

            end_match = match

            break

    if end_match:

        section = remaining[
            :end_match.start()
        ]

    else:

        section = remaining[
            :5000
        ]

    return normalize_text(
        section
    )


# ============================================================
# 8. EXTRACT WAITING VESSELS
# ============================================================

def extract_waiting_vessels(section):

    if not section:

        return 0

    section = normalize_text(
        section
    )

    lines = section.splitlines()

    vessels = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        line = normalize_vessel_prefix(
            line
        )

        # Normalize multiple spaces
        line = re.sub(
            r"[ \t]+",
            " ",
            line
        )

        # ----------------------------------------------------
        # Waiting rows have:
        #
        # priority + vessel type
        #
        # Examples:
        #
        # 1 MV. RED COSMOS
        # 1 MV. CHENNAI VALARCHI
        # 1 MT. GAS ALKHALEEJ
        # 2 MT. TORM SPLENDID
        #
        # ----------------------------------------------------

        match = re.match(
            r"^\s*\d+\s+(MV|MT)\s*\.",
            line,
            flags=re.IGNORECASE
        )

        if match:

            vessels.append(
                line
            )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    # Sometimes PDF extraction can remove the newline
    # between rows. In that case search the entire section.

    if len(vessels) == 0:

        normalized = re.sub(
            r"\s+",
            " ",
            section
        )

        pattern = (
            r"\b\d+\s+"
            r"(?:MV|MT)\s*\."
        )

        matches = re.findall(
            pattern,
            normalized,
            flags=re.IGNORECASE
        )

        vessels = matches

    # --------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------

    print(
        f"DEBUG waiting vessel entries: "
        f"{len(vessels)}"
    )

    if vessels:

        print(
            "DEBUG waiting vessels:"
        )

        for vessel in vessels:

            print(
                "   ",
                vessel[:150]
            )

    else:

        print(
            "DEBUG: No waiting vessels detected."
        )

        print(
            "DEBUG section preview:"
        )

        print(
            repr(section[:2000])
        )

    return len(vessels)


# ============================================================
# 9. GET WORKING / BERTHED SECTION
# ============================================================

def get_working_section(pages):

    full_text = get_full_text(
        pages
    )

    # Section A starts at the beginning of the report.

    start_patterns = [

        r"A\.\s*WORKING\s+VESSELS",

        r"A\.\s*VESSELS\s+WORKING"
    ]

    start_match = None

    for pattern in start_patterns:

        match = re.search(
            pattern,
            full_text,
            flags=re.IGNORECASE
        )

        if match:

            start_match = match

            break

    if start_match is None:

        print(
            "WARNING: Section A not found."
        )

        return ""

    remaining = full_text[
        start_match.end():
    ]

    # Section B ends Section A.

    end_patterns = [

        r"B\.\s*VESSELS\s+WAITING\s+AT\s+ANCHORAGE",

        r"B\.\s*VESSELS\s+WAITING"
    ]

    end_match = None

    for pattern in end_patterns:

        match = re.search(
            pattern,
            remaining,
            flags=re.IGNORECASE
        )

        if match:

            end_match = match

            break

    if end_match:

        section = remaining[
            :end_match.start()
        ]

    else:

        section = remaining[
            :20000
        ]

    return normalize_text(
        section
    )


# ============================================================
# 10. EXTRACT WORKING / BERTHED VESSELS
# ============================================================

def extract_berthed_vessels(section):

    if not section:

        return 0

    section = normalize_text(
        section
    )

    lines = section.splitlines()

    vessels = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        line = normalize_vessel_prefix(
            line
        )

        line = re.sub(
            r"[ \t]+",
            " ",
            line
        )

        # Working vessel rows normally contain:
        #
        # MV. MAESTRO
        # MV. APJ ANGAD
        # MT. GRANAT
        #
        # They are different from the waiting rows because
        # they don't necessarily start with a priority number.

        match = re.match(
            r"^(MV|MT)\s*\.\s+[A-Z]",
            line,
            flags=re.IGNORECASE
        )

        if match:

            vessels.append(
                line
            )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if len(vessels) == 0:

        normalized = re.sub(
            r"\s+",
            " ",
            section
        )

        pattern = (
            r"\b(?:MV|MT)\s*\.\s+[A-Z]"
        )

        matches = re.findall(
            pattern,
            normalized,
            flags=re.IGNORECASE
        )

        vessels = matches

    print(
        f"DEBUG working/berthed vessel entries: "
        f"{len(vessels)}"
    )

    return len(vessels)


# ============================================================
# 11. CONGESTION SCORE
# ============================================================

def calculate_congestion_score(
    berthed_vessels,
    waiting_vessels
):

    total = (
        berthed_vessels
        + waiting_vessels
    )

    if total == 0:

        return 0.0

    score = (
        waiting_vessels
        / total
    ) * 100

    return round(
        score,
        2
    )


# ============================================================
# 12. CONGESTION LEVEL
# ============================================================

def get_congestion_level(score):

    if score < 10:

        return "Low"

    elif score < 25:

        return "Moderate"

    elif score < 40:

        return "High"

    else:

        return "Severe"


# ============================================================
# 13. PROCESS ONE REPORT
# ============================================================

def process_report(
    date,
    url
):

    print(
        "\n" + "=" * 70
    )

    print(
        f"Processing {date.strftime('%Y-%m-%d')}"
    )

    print(
        "=" * 70
    )

    try:

        # ----------------------------------------------------
        # Download
        # ----------------------------------------------------

        pdf_bytes = download_pdf(
            url
        )

        print(
            f"PDF downloaded: "
            f"{len(pdf_bytes)} bytes"
        )

        # ----------------------------------------------------
        # Extract
        # ----------------------------------------------------

        pages = extract_pdf_pages(
            pdf_bytes
        )

        total_text = sum(
            len(page["text"])
            for page in pages
        )

        print(
            f"PDF pages: "
            f"{len(pages)}"
        )

        print(
            f"PDF text: "
            f"{total_text} characters"
        )

        # ----------------------------------------------------
        # WAITING VESSELS
        # ----------------------------------------------------

        waiting_section = get_waiting_section(
            pages
        )

        print(
            "DEBUG waiting section characters:",
            len(waiting_section)
        )

        waiting_vessels = extract_waiting_vessels(
            waiting_section
        )

        # ----------------------------------------------------
        # WORKING / BERTHED
        # ----------------------------------------------------

        working_section = get_working_section(
            pages
        )

        berthed_vessels = extract_berthed_vessels(
            working_section
        )

        # ----------------------------------------------------
        # CONGESTION
        # ----------------------------------------------------

        congestion_score = calculate_congestion_score(
            berthed_vessels,
            waiting_vessels
        )

        congestion_level = get_congestion_level(
            congestion_score
        )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        result = {

            "date":
                date.strftime(
                    "%Y-%m-%d"
                ),

            "port":
                PORT_NAME,

            "berthed_vessels":
                berthed_vessels,

            "waiting_vessels":
                waiting_vessels,

            "congestion_score":
                congestion_score,

            "congestion_level":
                congestion_level,

            "source":
                url
        }

        print(
            f"Working/Berthed: "
            f"{berthed_vessels}"
        )

        print(
            f"Waiting: "
            f"{waiting_vessels}"
        )

        print(
            f"Score: "
            f"{congestion_score}"
        )

        print(
            f"Level: "
            f"{congestion_level}"
        )

        return result

    except Exception as e:

        print(
            f"ERROR processing "
            f"{date.strftime('%Y-%m-%d')}: {e}"
        )

        return None


# ============================================================
# 14. SAVE HISTORY
# ============================================================

def save_history(records):

    if not records:

        print(
            "No records to save."
        )

        return

    df = pd.DataFrame(
        records
    )

    df["date"] = pd.to_datetime(
        df["date"]
    )

    df = df.sort_values(
        "date"
    )

    df = df.drop_duplicates(
        subset=[
            "date",
            "port"
        ],
        keep="last"
    )

    df["date"] = df["date"].dt.strftime(
        "%Y-%m-%d"
    )

    os.makedirs(
        os.path.dirname(
            OUTPUT_FILE
        ),
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "HISTORY SAVED"
    )

    print(
        "=" * 70
    )

    print(
        f"File: {OUTPUT_FILE}"
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Start: {df['date'].min()}"
    )

    print(
        f"End: {df['date'].max()}"
    )


# ============================================================
# 15. MAIN BACKFILL
# ============================================================

def main():

    print(
        "\n" + "=" * 70
    )

    print(
        "PARADIP PORT CONGESTION BACKFILL"
    )

    print(
        "=" * 70
    )

    reports = get_report_links()

    if not reports:

        print(
            "No reports found."
        )

        return

    records = []

    total = len(
        reports
    )

    for index, report in enumerate(
        reports,
        start=1
    ):

        print(
            f"\nREPORT {index}/{total}"
        )

        result = process_report(
            report["date"],
            report["url"]
        )

        if result is not None:

            records.append(
                result
            )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    save_history(
        records
    )

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    if records:

        df = pd.DataFrame(
            records
        )

        print(
            "\n" + "=" * 70
        )

        print(
            "FINAL SUMMARY"
        )

        print(
            "=" * 70
        )

        print(
            f"Reports processed: "
            f"{len(df)}"
        )

        print(
            f"Average waiting vessels: "
            f"{df['waiting_vessels'].mean():.2f}"
        )

        print(
            f"Average working/berthed vessels: "
            f"{df['berthed_vessels'].mean():.2f}"
        )

        print(
            f"Average congestion score: "
            f"{df['congestion_score'].mean():.2f}"
        )

        print(
            f"Maximum congestion score: "
            f"{df['congestion_score'].max():.2f}"
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()