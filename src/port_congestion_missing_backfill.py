import os
import re
import requests
import pandas as pd

from io import BytesIO
from pypdf import PdfReader


# ============================================================
# CONFIG
# ============================================================

TRAFFIC_PAGE = (
    "https://paradipport.gov.in/traffic/"
)

HISTORY_FILE = (
    "data/port_congestion_history.csv"
)

PORT_NAME = "Paradip"

MISSING_DATES = [
    "2026-07-06",
    "2026-07-26",
    "2026-07-30",
    "2026-08-14",
    "2026-08-15",
    "2026-08-16",
    "2026-08-18",
    "2026-08-20",
    "2026-08-22",
    "2026-09-02",
]


# ============================================================
# HTTP SESSION
# ============================================================

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/139.0 Safari/537.36"
    )
})


# ============================================================
# DOWNLOAD OFFICIAL TRAFFIC PAGE
# ============================================================

def get_traffic_page():

    response = session.get(
        TRAFFIC_PAGE,
        timeout=30
    )

    response.raise_for_status()

    return response.text


# ============================================================
# FIND PDF LINKS
# ============================================================

def find_pdf_urls(html):

    hrefs = re.findall(
        r'href\s*=\s*["\']([^"\']+\.pdf[^"\']*)["\']',
        html,
        flags=re.IGNORECASE
    )

    pdf_urls = []

    for href in hrefs:

        href = href.strip()

        if href.startswith("//"):

            url = "https:" + href

        elif href.startswith("http://"):

            url = href

        elif href.startswith("https://"):

            url = href

        elif href.startswith("/"):

            url = (
                "https://paradipport.gov.in"
                + href
            )

        else:

            url = (
                "https://paradipport.gov.in/"
                + href.lstrip("/")
            )

        pdf_urls.append(url)

    return list(
        dict.fromkeys(pdf_urls)
    )


# ============================================================
# EXTRACT DATE FROM URL
# ============================================================

def extract_date_from_url(url):

    filename = (
        url
        .split("?")[0]
        .split("/")[-1]
        .lower()
    )

    patterns = [

        # Standard report filename
        r"dtr(\d{2})(\d{2})\.pdf",

        # Variants used by the official Paradip traffic archive
        r"dtr(\d{2})(\d{2})[_-]+compressed\.pdf",
        r"dtr(\d{2})(\d{2})[_-]+compressed[^/]*\.pdf",

        # Older naming variants
        r"dtr[_-](\d{2})(\d{2})\.pdf",
        r"dtr[_-](\d{2})(\d{2})[_-]+compressed\.pdf"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            filename
        )

        if match:

            day = match.group(1)

            month = match.group(2)

            return (
                f"2026-{month}-{day}"
            )

    return None


# ============================================================
# GENERATE DIRECT URLS
# ============================================================

def generate_direct_urls(date):

    dt = pd.to_datetime(
        date
    )

    year = dt.strftime("%Y")

    month = dt.strftime("%m")

    day = dt.strftime("%d")

    filename = (
        f"dtr{day}{month}.pdf"
    )

    upper_filename = (
        f"DTR{day}{month}.pdf"
    )

    # Official Paradip archive also uses compressed PDFs.
    compressed_filename = (
        f"dtr{day}{month}_compressed.pdf"
    )

    compressed_upper_filename = (
        f"DTR{day}{month}_compressed.pdf"
    )

    # Some official reports use a double underscore.
    compressed_double_filename = (
        f"dtr{day}{month}__compressed.pdf"
    )

    compressed_double_upper_filename = (
        f"DTR{day}{month}__compressed.pdf"
    )

    urls = [

        # Current www path
        (
            f"https://www.paradipport.gov.in/"
            f"uploads/{year}/{month}/"
            f"{filename}"
        ),

        # Current non-www path
        (
            f"https://paradipport.gov.in/"
            f"uploads/{year}/{month}/"
            f"{filename}"
        ),

        # Uppercase filename
        (
            f"https://www.paradipport.gov.in/"
            f"uploads/{year}/{month}/"
            f"{upper_filename}"
        ),

        (
            f"https://paradipport.gov.in/"
            f"uploads/{year}/{month}/"
            f"{upper_filename}"
        ),

        # --------------------------------------------------------
        # Compressed filenames used by the official archive
        # --------------------------------------------------------

        (
            f"https://www.paradipport.gov.in/"
            f"uploads/{year}/{month}/"
            f"{compressed_filename}"
        ),

        (
            f"https://paradipport.gov.in/"
            f"uploads/{year}/{month}/"
            f"{compressed_filename}"
        ),

        (
            f"https://www.paradipport.gov.in/"
            f"uploads/{year}/{month}/"
            f"{compressed_upper_filename}"
        ),

        (
            f"https://paradipport.gov.in/"
            f"uploads/{year}/{month}/"
            f"{compressed_upper_filename}"
        ),

        (
            f"https://www.paradipport.gov.in/"
            f"uploads/{year}/{month}/"
            f"{compressed_double_filename}"
        ),

        (
            f"https://paradipport.gov.in/"
            f"uploads/{year}/{month}/"
            f"{compressed_double_filename}"
        ),

        (
            f"https://www.paradipport.gov.in/"
            f"uploads/{year}/{month}/"
            f"{compressed_double_upper_filename}"
        ),

        (
            f"https://paradipport.gov.in/"
            f"uploads/{year}/{month}/"
            f"{compressed_double_upper_filename}"
        ),

        # Legacy path
        (
            f"https://www.paradipport.gov.in/"
            f"Writereaddata/Daily_Traffic/"
            f"{filename}"
        ),

        (
            f"https://paradipport.gov.in/"
            f"Writereaddata/Daily_Traffic/"
            f"{filename}"
        ),

        # Legacy uppercase
        (
            f"https://www.paradipport.gov.in/"
            f"Writereaddata/Daily_Traffic/"
            f"{upper_filename}"
        ),

        (
            f"https://paradipport.gov.in/"
            f"Writereaddata/Daily_Traffic/"
            f"{upper_filename}"
        ),

        # Legacy compressed filenames
        (
            f"https://www.paradipport.gov.in/"
            f"Writereaddata/Daily_Traffic/"
            f"{compressed_filename}"
        ),

        (
            f"https://paradipport.gov.in/"
            f"Writereaddata/Daily_Traffic/"
            f"{compressed_filename}"
        ),

        (
            f"https://www.paradipport.gov.in/"
            f"Writereaddata/Daily_Traffic/"
            f"{compressed_double_filename}"
        ),

        (
            f"https://paradipport.gov.in/"
            f"Writereaddata/Daily_Traffic/"
            f"{compressed_double_filename}"
        )
    ]

    return list(
        dict.fromkeys(urls)
    )


# ============================================================
# CHECK IF URL IS A PDF
# ============================================================

def check_pdf_url(url):

    try:

        response = session.get(
            url,
            timeout=20,
            allow_redirects=True
        )

        if response.status_code != 200:

            return False

        if (
            response.content[:4]
            == b"%PDF"
        ):

            return True

    except Exception:

        pass

    return False


# ============================================================
# FIND URL FOR DATE
# ============================================================

def find_url_for_date(
    date,
    pdf_urls
):

    # --------------------------------------------------------
    # 1. Search official traffic page URLs
    # --------------------------------------------------------

    for url in pdf_urls:

        url_date = (
            extract_date_from_url(
                url
            )
        )

        if url_date == date:

            return url

    # --------------------------------------------------------
    # 2. Try direct URL candidates
    # --------------------------------------------------------

    candidates = (
        generate_direct_urls(
            date
        )
    )

    for url in candidates:

        print(
            f"  Trying: {url}"
        )

        if check_pdf_url(
            url
        ):

            return url

    return None


# ============================================================
# DOWNLOAD PDF
# ============================================================

def download_pdf(url):

    response = session.get(
        url,
        timeout=30,
        allow_redirects=True
    )

    response.raise_for_status()

    if (
        response.content[:4]
        != b"%PDF"
    ):

        raise ValueError(
            "Downloaded file is not a PDF."
        )

    return response.content


# ============================================================
# EXTRACT PDF TEXT
# ============================================================

def extract_pdf_text(
    pdf_bytes
):

    reader = PdfReader(
        BytesIO(pdf_bytes)
    )

    pages = []

    for page in reader.pages:

        try:

            text = page.extract_text(
                extraction_mode="layout"
            )

        except TypeError:

            text = page.extract_text()

        if text:

            pages.append(
                text
            )

    return "\n".join(
        pages
    )


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    text = text.replace(
        "\xa0",
        " "
    )

    text = text.replace(
        "\r",
        "\n"
    )

    return text


# ============================================================
# GET SECTION B
# ============================================================

def get_waiting_section(
    text
):

    text = normalize_text(
        text
    )

    # --------------------------------------------------------
    # Find Section B
    # --------------------------------------------------------

    start_patterns = [

        r"B\.\s*VESSELS?\s+WAITING\s+AT\s+ANCHORAGE",

        r"B\.\s*VESSELS?\s+WAITING",

        r"VESSELS?\s+WAITING\s+AT\s+ANCHORAGE"
    ]

    start_position = None

    for pattern in start_patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            start_position = (
                match.end()
            )

            break

    if start_position is None:

        print(
            "WARNING: Section B not found."
        )

        return ""

    # --------------------------------------------------------
    # Find Section C
    # --------------------------------------------------------

    end_patterns = [

        r"C\.\s*EXPECTED\s+VES+SEL",

        r"C\.\s*EXPECTED",

        r"EXPECTED\s+VES+SEL"
    ]

    end_position = len(
        text
    )

    remaining_text = text[
        start_position:
    ]

    for pattern in end_patterns:

        match = re.search(
            pattern,
            remaining_text,
            flags=re.IGNORECASE
        )

        if match:

            end_position = (
                start_position
                +
                match.start()
            )

            break

    return text[
        start_position:end_position
    ]


# ============================================================
# EXTRACT WAITING VESSELS
# ============================================================

def extract_waiting_vessels(
    text
):

    section = get_waiting_section(
        text
    )

    if not section:

        return 0

    print(
        f"Waiting section characters: "
        f"{len(section)}"
    )

    # --------------------------------------------------------
    # Layout mode usually keeps each vessel entry separate.
    #
    # Example:
    #
    # 1 MV. RED COSMOS
    # 2 MT. TORM SPLENDID
    #
    # --------------------------------------------------------

    patterns = [

        re.compile(
            r"(?:^|\n)"
            r"\s*\d+\s+"
            r"(?:MV|MT)\."
            r"\s*"
            r"[A-Z0-9][A-Z0-9 .&()'/_-]*",
            flags=re.IGNORECASE
        ),

        re.compile(
            r"\b\d+\s+"
            r"(?:MV|MT)\."
            r"\s*"
            r"[A-Z0-9][A-Z0-9 .&()'/_-]*",
            flags=re.IGNORECASE
        )
    ]

    matches = []

    for pattern in patterns:

        matches = pattern.findall(
            section
        )

        if matches:

            break

    vessels = []

    for match in matches:

        vessel = (
            match
            .strip()
            .upper()
        )

        vessel = re.sub(
            r"\s+",
            " ",
            vessel
        )

        if vessel not in vessels:

            vessels.append(
                vessel
            )

    print(
        f"DEBUG waiting vessel entries: "
        f"{len(vessels)}"
    )

    return len(vessels)


# ============================================================
# EXTRACT WORKING / BERTHED VESSELS
# ============================================================

def extract_working_vessels(
    text
):

    text = normalize_text(
        text
    )

    # --------------------------------------------------------
    # Section A ends when Section B begins.
    # --------------------------------------------------------

    section_a_match = re.search(
        r"A\..*?(?=B\.)",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not section_a_match:

        print(
            "WARNING: Section A not found."
        )

        return 0

    section_a = (
        section_a_match.group(0)
    )

    pattern = re.compile(
        r"\b(?:MV|MT)\."
        r"\s*"
        r"[A-Z0-9][A-Z0-9 .&()'/_-]*",
        flags=re.IGNORECASE
    )

    matches = pattern.findall(
        section_a
    )

    vessels = []

    for match in matches:

        vessel = (
            match
            .strip()
            .upper()
        )

        vessel = re.sub(
            r"\s+",
            " ",
            vessel
        )

        if vessel not in vessels:

            vessels.append(
                vessel
            )

    return len(vessels)


# ============================================================
# CONGESTION SCORE
# ============================================================

def calculate_congestion_score(
    berthed,
    waiting
):

    total = (
        berthed
        +
        waiting
    )

    if total <= 0:

        return 0.0

    return (
        waiting
        /
        total
    ) * 100


# ============================================================
# CONGESTION LEVEL
# ============================================================

def get_congestion_level(
    score
):

    if score < 10:

        return "Low"

    elif score < 25:

        return "Moderate"

    elif score < 40:

        return "High"

    else:

        return "Severe"


# ============================================================
# PROCESS REPORT
# ============================================================

def process_report(
    date,
    url
):

    print(
        "\n" + "-" * 70
    )

    print(
        f"Processing: {date}"
    )

    print(
        f"URL: {url}"
    )

    try:

        pdf_bytes = download_pdf(
            url
        )

        print(
            f"PDF downloaded: "
            f"{len(pdf_bytes)} bytes"
        )

        text = extract_pdf_text(
            pdf_bytes
        )

        print(
            f"PDF text: "
            f"{len(text)} characters"
        )

        berthed = (
            extract_working_vessels(
                text
            )
        )

        waiting = (
            extract_waiting_vessels(
                text
            )
        )

        score = (
            calculate_congestion_score(
                berthed,
                waiting
            )
        )

        level = (
            get_congestion_level(
                score
            )
        )

        print(
            f"Working/Berthed: "
            f"{berthed}"
        )

        print(
            f"Waiting: "
            f"{waiting}"
        )

        print(
            f"Score: "
            f"{score:.2f}"
        )

        print(
            f"Level: "
            f"{level}"
        )

        # ----------------------------------------------------
        # Prevent adding completely failed parses
        # ----------------------------------------------------

        if (
            berthed == 0
            and
            waiting == 0
        ):

            print(
                "WARNING: "
                "No vessels detected."
            )

            print(
                "Row NOT added."
            )

            return None

        return {

            "date":
                date,

            "port":
                PORT_NAME,

            "berthed_vessels":
                berthed,

            "waiting_vessels":
                waiting,

            "congestion_score":
                round(
                    score,
                    2
                ),

            "congestion_level":
                level,

            "source":
                url
        }

    except Exception as error:

        print(
            f"ERROR processing {date}:"
        )

        print(
            error
        )

        return None


# ============================================================
# UPDATE HISTORY CSV
# ============================================================

def update_history(
    rows
):

    if not rows:

        print(
            "\nNo new valid rows to add."
        )

        return

    new_df = pd.DataFrame(
        rows
    )

    # --------------------------------------------------------
    # Existing CSV
    # --------------------------------------------------------

    if os.path.exists(
        HISTORY_FILE
    ):

        old_df = pd.read_csv(
            HISTORY_FILE
        )

    else:

        old_df = pd.DataFrame()

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    combined = pd.concat(
        [
            old_df,
            new_df
        ],
        ignore_index=True
    )

    # --------------------------------------------------------
    # Date conversion
    # --------------------------------------------------------

    combined["date"] = pd.to_datetime(
        combined["date"],
        errors="coerce"
    )

    combined = combined.dropna(
        subset=[
            "date"
        ]
    )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    combined = (
        combined
        .drop_duplicates(
            subset=[
                "date",
                "port"
            ],
            keep="last"
        )
        .sort_values(
            "date"
        )
        .reset_index(
            drop=True
        )
    )

    # --------------------------------------------------------
    # Save standard date format
    # --------------------------------------------------------

    combined["date"] = (
        combined["date"]
        .dt.strftime(
            "%Y-%m-%d"
        )
    )

    combined.to_csv(
        HISTORY_FILE,
        index=False
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "HISTORY UPDATED"
    )

    print(
        "=" * 70
    )

    print(
        f"Rows now: "
        f"{len(combined)}"
    )

    print(
        f"Saved: "
        f"{HISTORY_FILE}"
    )


# ============================================================
# FINAL VALIDATION
# ============================================================

def validate_history():

    if not os.path.exists(
        HISTORY_FILE
    ):

        print(
            "History file does not exist."
        )

        return

    df = pd.read_csv(
        HISTORY_FILE
    )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["date"]
    )

    dates = (
        df["date"]
        .sort_values()
        .drop_duplicates()
    )

    expected = pd.date_range(
        start=dates.min(),
        end=dates.max(),
        freq="D"
    )

    missing = (
        expected
        .difference(
            dates
        )
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "FINAL VALIDATION"
    )

    print(
        "=" * 70
    )

    print(
        f"Total rows: "
        f"{len(df)}"
    )

    print(
        f"Start: "
        f"{dates.min().date()}"
    )

    print(
        f"End: "
        f"{dates.max().date()}"
    )

    print(
        f"Missing dates remaining: "
        f"{len(missing)}"
    )

    if len(missing) > 0:

        for date in missing:

            print(
                f"  "
                f"{date.strftime('%Y-%m-%d')}"
            )

    else:

        print(
            "All dates are present."
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "=" * 70
    )

    print(
        "PARADIP MISSING REPORT BACKFILL"
    )

    print(
        "=" * 70
    )

    # --------------------------------------------------------
    # Official traffic page
    # --------------------------------------------------------

    print(
        "\nDownloading official traffic page..."
    )

    try:

        html = get_traffic_page()

    except Exception as error:

        print(
            "Could not download official "
            "traffic page:"
        )

        print(
            error
        )

        raise SystemExit

    print(
        "Traffic page downloaded."
    )

    # --------------------------------------------------------
    # Find PDF links
    # --------------------------------------------------------

    pdf_urls = find_pdf_urls(
        html
    )

    print(
        f"PDF links found: "
        f"{len(pdf_urls)}"
    )

    # --------------------------------------------------------
    # Process missing dates
    # --------------------------------------------------------

    new_rows = []

    for date in MISSING_DATES:

        print(
            "\n" + "=" * 70
        )

        print(
            f"Finding report for: "
            f"{date}"
        )

        url = find_url_for_date(
            date,
            pdf_urls
        )

        if url is None:

            print(
                f"NOT FOUND: {date}"
            )

            continue

        print(
            f"Found URL:"
        )

        print(
            url
        )

        result = process_report(
            date,
            url
        )

        if result:

            new_rows.append(
                result
            )

    # --------------------------------------------------------
    # Update CSV
    # --------------------------------------------------------

    update_history(
        new_rows
    )

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    validate_history()