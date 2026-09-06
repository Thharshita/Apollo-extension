import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from scrapers.web_scraper_selenium import selenium_fetch_links, extract_contents_selenium
from tenacity import retry, stop_after_attempt, wait_exponential
from constant import PROXY, UNWANTED_DOMAINS, UNWANTED_PREFIXES, UNWANTED_URLS
from typing import Tuple, List, Any, Dict
from logger import logger
from utils import extract_name_number_designation

REQUEST_PROXIES = PROXY or {"http": None, "https": None}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_links(url) -> Tuple[int, List[str], str]:
    """
    Fetches links from a URL with retries.

    Args:
        url (str): URL to fetch links from.

    Returns:
        Tuple[int, List[str], str]: Link status, list of links, and Selenium usage indicator.
    """
    try:
        logger.info("Fetching links")
        selenium="NO"
        
        response = requests.get(url,
            proxies=REQUEST_PROXIES,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10)
        
        # Check response status code
        if response.status_code != 200:
            return 0, {"status": 0, "message": f"Invalid status code: {response.status_code}", "result": "Link is not valid"}, "NO"
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        if response.status_code == 200:
            list_of_links=[url]
            
            links = soup.find_all('a', href=True)
            # logger.info(f"links:{links}")
            extracted_links = [urljoin(url, link['href']) for link in links if is_valid_link(url, link['href'])]
            
            # Check if links require Selenium
            if "https://www.enable-javascript.com/" in extracted_links or not extracted_links:
                logger.info("Passing to selenium for link extraction")
                selenium='YES'
                link_status, list_links= await selenium_fetch_links(url)
                return link_status, list_links, selenium

            list_of_links = [url] + extracted_links 
            list_of_links=set(list_of_links)
            final_list_of_links=list(list_of_links)
            
            logger.info(f"extracted_links:{final_list_of_links}")
            # logger.info(f"extracted_links lenght:{len(final_list_of_links)}")
           
            return 1, final_list_of_links, selenium

    except Exception as e:
        logger.error(f"Error while fetching link{url}: {str(e)}")
        logger.info("Trying Selenium after failing BeautifulSoup")
        
        selenium='YES'
        link_status, list_links= await selenium_fetch_links(url)
        return link_status, list_links, selenium



def is_valid_link(base_url: str, link: str) -> bool:
    """
    Checks if a link is valid.

    Args:
        base_url (str): Base URL.
        link (str): Link to validate.

    Returns:
        bool: True if link is valid, False otherwise.
    """
    # logger.info("\nValidating link")
    
    if link.startswith(tuple(UNWANTED_PREFIXES)) or any(domain in link for domain in UNWANTED_DOMAINS) or link in UNWANTED_URLS:
        return False
    
    if not link.startswith('http'): #which is just a path , not a complete link
        link = urljoin(base_url, link)
    
    # logger.info(f"base_url: {base_url}")
    # logger.info(f"link: {link}")
    
    parsed_link = urlparse(link)
    base_domain = urlparse(base_url).netloc
    # logger.info(f"parsed_link netloc:{parsed_link.netloc}")
    # logger.info(f"base_domain netloc: {base_domain}")
    
    # if parsed_link.netloc != base_domain and not parsed_link.netloc.endswith('.' + base_domain):
    if parsed_link.netloc != base_domain :
        return False
    
    return True

def _scrape_contact_info(link: str) -> dict:
    try:
        logger.info(f"Scraping contact info from: {link}")
        response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code != 200:
            logger.info(f"Failed to get the response")
            return {}
        
        soup = BeautifulSoup(response.content, 'html.parser')
        # logger.info(f"soup:{soup}")

        for tag in soup.find_all(['header', 'footer', 'title']):
            tag.decompose()

        text_content = soup.get_text(separator=' ', strip=True)
        return extract_name_number_designation(text_content)
    except Exception as e:
        logger.error(f"Failed to scrape contact info from {link}: {e}")
        return {}


def _is_contact_link(link: str) -> bool:
    normalized = re.sub(r'[-_\s./]+', '', link.lower())
    return bool(re.search(
        r'(?:contact(?:us|s)?|getintouch|reach(?:out)?(?:us)?|talkto(?:us)?|connect(?:with)?(?:us)?)',
        normalized,
    ))

async def extract_contents(links: List[str], use_selenium: str, crawl_link: str) -> Dict[str, Any]:

    try:
        logger.info("Inside extract content")
        logger.info(f"Links: {links}, use_selenium: {use_selenium}")

        if use_selenium == "YES":
            return await extract_contents_selenium(links, crawl_link)

        contact_links = [l for l in links if _is_contact_link(l)]
        other_links = [l for l in links if not _is_contact_link(l)]

        logger.info(f"Contact links found: {contact_links}")
        logger.info(f"Other links found: {other_links}")

        # Try contact links first
        information=[]
        found_email = None
        found_number = None

        for link in contact_links:
            info = _scrape_contact_info(link)
            if any(info.values()):
                logger.info(f"Contact info found in: {link}, info: {info}")
                information.append({"link": link, **info})
            found_email = found_email or info.get("email")
            found_number = found_number or info.get("number")
            if found_email and found_number:
                logger.info("Both email and number found, stopping.")
                return information
                

        # Fallback to other links
        # for link in other_links[:15]:
        #     info = _scrape_contact_info(link)
        #     if any(info.values()):
        #         logger.info(f"Contact info found in fallback link: {link}")
        #         information.append({"link": link, **info})
        #     found_email = found_email or info.get("email")
        #     found_number = found_number or info.get("number")
        #     if found_email and found_number:
        #         logger.info("Both email and number found, stopping.")
        #         break
        # logger.info(f"metrics: {information}")
        
        return information

    except Exception as e:
        logger.error(f"An error occurred while crawling raw text website: {str(e)}")
        return {"status": 0, "message": "Unable to process text", "result": str(e)}


async def check_link(url):
    try:
        logger.info("Checking links")
        logger.info(f"url: {url}")
        selenium="NO"

        response = requests.get(url,
            proxies=REQUEST_PROXIES,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10)
        
        # Check response status code
        if response.status_code != 200:
            return 0, {"status": 0, "message": f"Invalid status code: {response.status_code}", "result": "Link is not valid"}, "NO"
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        if response.status_code == 200:
            list_of_links=[url]
            
            links = soup.find_all('a', href=True)
            #logger.info(f"links:{links}")
            extracted_links = [urljoin(url, link['href']) for link in links if is_valid_link(url, link['href'])]
            
            # Check if links require Selenium
            if "https://www.enable-javascript.com/" in extracted_links or not extracted_links:
                logger.info("Passing to selenium for link extraction")
                selenium='YES'
    
            return 1, list_of_links, selenium

    except Exception as e:
        logger.error(f"Error while fetching link{url}: {str(e)}")
        logger.info("Trying Selenium after failing BeautifulSoup")
        
        selenium='YES'
        return 1, list_of_links, selenium
