import os
import json
import requests
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Gemini client
client = genai.Client(
    api_key=os.getenv("MAISSA_GEMINI_API_KEY")
)


# --------------------------------------------------
# EXTRACT ONE SCHEME USING GEMINI
# --------------------------------------------------

def extract_scheme_with_gemini(scheme_url):

    print("\nProcessing:")
    print(scheme_url)

    # ----------------------------------------------
    # Download webpage
    # ----------------------------------------------

    response = requests.get(
        scheme_url,
        timeout=20
    )

    response.raise_for_status()

    # ----------------------------------------------
    # Extract webpage text
    # ----------------------------------------------

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Remove unnecessary elements
    for tag in soup([
        "script",
        "style",
        "nav",
        "footer"
    ]):
        tag.decompose()

    scheme_text = soup.get_text(
        " ",
        strip=True
    )

    # Limit text sent to Gemini
    scheme_text = scheme_text[:20000]

    print("\n--- SCHEME TEXT ---\n")
    print(scheme_text[:1000])

    # ----------------------------------------------
    # Gemini prompt
    # ----------------------------------------------

    prompt = f"""
You are an AI government-scheme information extraction system.

Read the following government scheme webpage text.

Extract the information into JSON.

Required fields:

- name
- project_type
- max_project_cost
- income_limit
- education_status
- max_loan
- target_groups
- source_url

Rules:

- Do not invent information.
- If information is not available, use null.
- If the scheme explicitly says there is no income limit, use null.
- project_type can contain:
  business, education, income-generating
- education_status can contain:
  student, not_required, required
- Return ONLY valid JSON.

SOURCE URL:
{scheme_url}

WEBPAGE TEXT:
{scheme_text}
"""

    # ----------------------------------------------
    # Call Gemini
    # Handle 503 errors
    # ----------------------------------------------

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            # Gemini request successful
            break

        except Exception as e:

            error_message = str(e)

            # ------------------------------
            # 503 = Gemini temporarily busy
            # ------------------------------

            if "503" in error_message:

                if attempt < 2:

                    print(
                        "\nGemini is busy."
                    )

                    print(
                        f"Retrying in 5 seconds..."
                        f" (Attempt {attempt + 1}/3)"
                    )

                    time.sleep(5)

                else:

                    print(
                        "\nGemini still unavailable "
                        "after 3 attempts."
                    )

                    raise

            # ------------------------------
            # 429 = Quota exceeded
            # ------------------------------

            elif "429" in error_message:

                print(
                    "\nGemini API quota exceeded."
                )

                print(
                    "Stopping further Gemini extraction."
                )

                # Send error back to main loop
                raise

            # ------------------------------
            # Other errors
            # ------------------------------

            else:

                raise

    # ----------------------------------------------
    # Clean Gemini response
    # ----------------------------------------------

    result = response.text.strip()

    # Remove markdown code fences if Gemini adds them
    result = result.replace(
        "```json",
        ""
    )

    result = result.replace(
        "```",
        ""
    )

    result = result.strip()

    # ----------------------------------------------
    # Convert JSON string to Python dictionary
    # ----------------------------------------------

    scheme = json.loads(result)

    return scheme


# --------------------------------------------------
# FIND SCHEME LINKS FROM GOVERNMENT LISTING PAGE
# --------------------------------------------------

def get_scheme_links(listing_url):

    response = requests.get(
        listing_url,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    links = soup.find_all(
        "a",
        href=True
    )

    scheme_links = []

    for link in links:

        href = link.get(
            "href",
            ""
        )

        # Only collect individual scheme pages
        if "/en/scheme/" in href:

            scheme_links.append(href)

    # Remove duplicate URLs
    scheme_links = list(
        dict.fromkeys(scheme_links)
    )

    return scheme_links


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    # ----------------------------------------------
    # Ask user for government listing page
    # ----------------------------------------------

    listing_url = input(
        "Enter government scheme URL: "
    )

    try:

        # ------------------------------------------
        # Find scheme URLs
        # ------------------------------------------

        scheme_links = get_scheme_links(
            listing_url
        )

        print(
            "\n--- SCHEME LINKS FOUND ---\n"
        )

        for url in scheme_links:

            print(url)

        print(
            "\nTotal schemes found:",
            len(scheme_links)
        )

        # ------------------------------------------
        # Store successfully extracted schemes
        # ------------------------------------------

        all_schemes = []

        # ------------------------------------------
        # Process each scheme
        # ------------------------------------------

        for scheme_url in scheme_links:

            try:

                scheme = extract_scheme_with_gemini(
                    scheme_url
                )

                # Save successful extraction
                all_schemes.append(
                    scheme
                )

                print(
                    "\nAI EXTRACTED SCHEME:"
                )

                print(
                    json.dumps(
                        scheme,
                        indent=4
                    )
                )

            except Exception as e:

                print(
                    "\nERROR processing:"
                )

                print(
                    scheme_url
                )

                print(
                    e
                )

                # ----------------------------------
                # If quota exceeded, STOP
                # ----------------------------------

                if "429" in str(e):

                    print(
                        "\n================================"
                    )

                    print(
                        "Gemini quota exceeded."
                    )

                    print(
                        "Stopping further AI extraction."
                    )

                    print(
                        "Already extracted schemes "
                        "will still be saved."
                    )

                    print(
                        "================================"
                    )

                    break

                # ----------------------------------
                # Other errors:
                # continue with next scheme
                # ----------------------------------

                continue

        # ------------------------------------------
        # Save extracted schemes
        # ------------------------------------------

        with open(
            "extracted_schemes.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                all_schemes,
                file,
                indent=4,
                ensure_ascii=False
            )

        # ------------------------------------------
        # Final result
        # ------------------------------------------

        print(
            "\n================================"
        )

        print(
            "DONE!"
        )

        print(
            "Total schemes extracted:",
            len(all_schemes)
        )

        print(
            "Saved to: extracted_schemes.json"
        )

        print(
            "================================"
        )

    except Exception as e:

        print(
            "\nError:"
        )

        print(e)