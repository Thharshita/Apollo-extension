# ── OLD SELENIUM GOOGLE SCRAPER (commented out — Google blocks headless Selenium with CAPTCHA) ──
# import time
# import re
# from bs4 import BeautifulSoup
# from logger import logger
# from utils import extract_name_number_designation
#
# def google_search(company_name: str) -> dict:
#     from selenium import webdriver
#     result = {"email": None, "number": None, "website": None}
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option('excludeSwitches', ['enable-automation'])
#     options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
#     driver = webdriver.Chrome(options=options)
#     try:
#         logger.info(f"Performing Google search for company: {company_name}")
#         query = company_name.strip().replace(" ", "+")
#         driver.get(f"https://www.google.com/search?q={query}")
#         time.sleep(3)
#         soup = BeautifulSoup(driver.page_source, 'html.parser')
#         text = soup.get_text(separator=' ', strip=True)
#         extracted = extract_name_number_designation(text)
#         result["email"] = extracted.get("email")
#         result["number"] = extracted.get("number")
#         for a in soup.find_all('a', href=True):
#             href = a['href']
#             if '/url?q=' in href:
#                 actual = href.split('/url?q=')[1].split('&')[0]
#                 if (actual.startswith('http') and 'google.com' not in actual
#                         and 'youtube.com' not in actual and 'facebook.com' not in actual
#                         and 'linkedin.com' not in actual and 'twitter.com' not in actual):
#                     result["website"] = actual
#                     break
#         logger.info(f"Google result for '{company_name}': {result}")
#     except Exception as e:
#         logger.error(f"Google search error for '{company_name}': {e}")
#     finally:
#         driver.quit()
#     return result
# ── END OLD SCRAPER ──


from logger import logger
from utils import extract_name_number_designation


UNWANTED_DOMAINS = ['google.com', 'youtube.com', 'facebook.com', 'linkedin.com',
                    'twitter.com', 'instagram.com', 'wikipedia.org', 'justdial.com',
                    'indiamart.com', 'tradeindia.com']


# def google_search(company_name: str, known_website: str = None) -> dict:
#     """
#     Uses duckduckgo-search to find company info.
#     If known_website is provided, uses site: operator to restrict results to that domain only.
#     Otherwise falls back to company name search and picks first non-directory URL.
#     """
#     from ddgs import DDGS
#     from urllib.parse import urlparse

#     result = {"email": None, "number": None, "website": None}

#     try:
#         if known_website:
#             domain = urlparse(known_website).netloc.lstrip("www.")
#             query = f'"{company_name}" site:{domain} email and contact number'
            
#         else:
#             query = f'"{company_name}" email and contact number'

#         with DDGS() as ddgs:
#             results = list(ddgs.text(query, max_results=10))
            
#         logger.info(f"DDG search query: {query}")
#         logger.info(f"DDG search result: {results}")

#         logger.info(f"DDG results count: {len(results)}")

#         combined_text = " ".join([r.get("body", "") + " " + r.get("title", "") for r in results])
#         logger.info(f"DDG combined snippet text: {combined_text[:500]}")

#         extracted = extract_name_number_designation(combined_text)
#         result["email"] = extracted.get("email")
#         result["number"] = extracted.get("number")

#         # Only resolve website from results if not already known — use 1st result as most relevant
#         if not known_website and results:
#             result["website"] = results[0].get("href")

#         logger.info(f"DDG result for '{company_name}': {result}")

#     except Exception as e:
#         logger.error(f"DuckDuckGo search error for '{company_name}': {e}")

#     return result


def google_search(company_name: str, known_website: str = None) -> dict:
    from ddgs import DDGS
    from urllib.parse import urlparse

    result = {
        "email": None,
        "number": None,
        "website": None
    }

    IGNORED_DOMAINS = {
        "linkedin.com",
        "facebook.com",
        "instagram.com",
        "twitter.com",
        "x.com",
        "youtube.com",
        "zoominfo.com",
        "rocketreach.co",
        "contactout.com",
        "growjo.com",
        "leadnear.com",
        "prospeo.io",
        "apollo.io",
        "crunchbase.com",
        "volza.com",
        "scribd.com",
        "slideshare.net",
        "justdial.com",
        "yelp.com",
    }

    def get_domain(url):
        try:
            return urlparse(url).netloc.lower().removeprefix("www.")
        except Exception:
            return ""

    def is_ignored(url):
        domain = get_domain(url)

        return any(
            domain == ignored or domain.endswith("." + ignored)
            for ignored in IGNORED_DOMAINS
        )

    try:

        if known_website:

            domain = get_domain(known_website)

            query = (
                f'"{company_name}" '
                f'site:{domain} email phone'
            )

        else:

            query = (
                f'"{company_name}" '
                f'"official website"'
            )

        logger.info(f"DDG query: {query}")

        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    query,
                    max_results=10
                )
            )

        # logger.info(f"DDG results count: {len(results)}")


        for r in results:

            href = r.get("href", "")

            if not href:
                continue

            # Ignore directories/social/etc.
            if is_ignored(href):
                continue

            # If website already known, result MUST
            # belong to that domain
            if known_website:

                result_domain = get_domain(href)

                if result_domain != domain:
                    continue

            # First acceptable result
            result["website"] = href

            text = (
                r.get("title", "")
                + " "
                + r.get("body", "")
            )

            logger.info(
                f"Using FIRST valid result: {href} -- text snippet: {text[:200]}..."
            )

            extracted = extract_name_number_designation(text)

            result["email"] = extracted.get("email")
            result["number"] = extracted.get("number")

            break

        logger.info(
            f"Final DDG result for '{company_name}': {result}"
        )

    except Exception as e:

        logger.error(
            f"DuckDuckGo search error for "
            f"'{company_name}': {e}"
        )

    return result


def duckduckgo_search(query: str, max_results: int = 10) -> list:
    """Return raw DuckDuckGo text results for a query."""
    from ddgs import DDGS

    logger.info(f"DuckDuckGo search query: {query}")
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))

    logger.info(f"DuckDuckGo results count: {len(results)}")
    return results



# def google_search(
#     company_name: str,
#     known_website: str = None,
#     company_linkedin: str = None,
#     city: str = None,
#     state: str = None,
#     country: str = None,
#     industry: str = None,
#     company_address: str = None
# ) -> dict:

#     from ddgs import DDGS
#     from urllib.parse import urlparse

#     result = {
#         "email": None,
#         "number": None,
#         "website": None
#     }

#     IGNORED_DOMAINS = {
#         "linkedin.com",
#         "facebook.com",
#         "instagram.com",
#         "twitter.com",
#         "x.com",
#         "youtube.com",
#         "zoominfo.com",
#         "rocketreach.co",
#         "contactout.com",
#         "growjo.com",
#         "leadnear.com",
#         "prospeo.io",
#         "apollo.io",
#         "crunchbase.com",
#         "volza.com",
#         "scribd.com",
#         "slideshare.net",
#         "justdial.com",
#         "yelp.com",
#     }

#     def get_domain(url):
#         try:
#             return urlparse(url).netloc.lower().removeprefix("www.")
#         except Exception:
#             return ""

#     def is_ignored(url):
#         domain = get_domain(url)

#         return any(
#             domain == ignored or domain.endswith("." + ignored)
#             for ignored in IGNORED_DOMAINS
#         )

#     try:

#         # ------------------------------------------------
#         # Build company identity
#         # ------------------------------------------------

#         identity = f'"{company_name}"'

#         if city:
#             identity += f' "{city}"'

#         if state:
#             identity += f' "{state}"'

#         if country:
#             identity += f' "{country}"'

#         if industry:
#             identity += f' "{industry}"'

#         # ------------------------------------------------
#         # CASE 1: Website already available
#         # ------------------------------------------------

#         if known_website:

#             domain = get_domain(known_website)

#             result["website"] = known_website

#             query = (
#                 f'{identity} '
#                 f'site:{domain} email phone'
#             )

#         # ------------------------------------------------
#         # CASE 2: Website not available
#         # ------------------------------------------------

#         else:

#             query = (
#                 f'{identity} '
#                 f'"official website" email phone'
#             )

#         logger.info(f"DDG query: {query}")

#         with DDGS() as ddgs:
#             results = list(
#                 ddgs.text(
#                     query,
#                     max_results=10
#                 )
#             )

#         logger.info(f"DDG results count: {len(results)}")

#         # ------------------------------------------------
#         # ONLY USE FIRST VALID RESULT
#         # ------------------------------------------------

#         for r in results:

#             href = r.get("href", "")

#             if not href:
#                 continue

#             # Ignore directories/social/etc.
#             if is_ignored(href):
#                 continue

#             # If website already known, result MUST
#             # belong to that domain
#             if known_website:

#                 result_domain = get_domain(href)

#                 if result_domain != domain:
#                     continue

#             text = (
#                 r.get("title", "")
#                 + " "
#                 + r.get("body", "")
#             )

#             # ------------------------------------------------
#             # Make sure result is related to the company
#             # ------------------------------------------------

#             company_match = company_name.lower() in text.lower()

#             if not company_match:
#                 continue

#             # ------------------------------------------------
#             # First acceptable result
#             # ------------------------------------------------

#             result["website"] = result["website"] or href

#             logger.info(
#                 f"Using FIRST valid result: {href}"
#             )

#             extracted = extract_name_number_designation(text)

#             result["email"] = extracted.get("email")
#             result["number"] = extracted.get("number")

#             break

#         logger.info(
#             f"Final DDG result for '{company_name}': {result}"
#         )

#     except Exception as e:

#         logger.error(
#             f"DuckDuckGo search error for "
#             f"'{company_name}': {e}"
#         )

#     return result