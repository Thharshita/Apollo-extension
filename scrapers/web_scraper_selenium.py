from bs4 import BeautifulSoup
from urllib.parse import urljoin
from logger import logger 
from urllib.parse import urljoin, urlparse
import time
from typing import List
from utils import process_tat, extract_name_number_designation

# https://myexternalip.com/raw
import random
# def rand_proxy():
#     proxy= random.choice(ips)
#     return proxy

#fetch_links_using_selenium
async def selenium_fetch_links(url)-> tuple[int, List[str], str]:
    """
    Fetches links from a URL using Selenium.

    Args:
        url (str): URL to fetch links from.

    Returns:
        Tuple[int, List[str]]: Link status and list of links.
    """

    from selenium.webdriver.common.by import By
    import time
    from constant import ips
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    try:
        logger.info(f"Fetching links from {url} using Selenium")

        driver.get(url)
        time.sleep(3)
        driver.implicitly_wait(15)

        page_source = driver.page_source
        driver.quit()

        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Parse HTML content
        links = soup.find_all('a', href=True)
        # logger.info(f"all links: {links}")
        # logger.info("links: {}".format(links))

        extracted_links = [urljoin(url, link['href']) for link in links if is_valid_link(url, link['href'])]
        
        # Keep discovery order so the first contact page is scraped first.
        list_of_links = list(dict.fromkeys([url] + extracted_links))
        
        logger.info("list_of_links from selenium: {}".format(list_of_links))

        return 1, list_of_links
    
    except Exception as e:
        logger.error(f"An error occurred while fetching through selenium: {str(e)}")
        return 0, {"status":0, "message":"", "result":str(e)}
  

def is_valid_link(base_url, link):
    # logger.info(f"checking validity for link:{link}")
    if (link.startswith('#') and not link.startswith('#/')) or link.startswith('javascript:') or link.startswith('mailto:') or link.startswith("tel:"):
        return False
    if 'maps.app.goo.gl' in link:  
        return False
    if 'google.com/maps' in link:   
        return False
    if any(domain in link for domain in ['.pdf','.zip', 'xlsx','.jpg',
            'play.google.com','instagram.com','dlai.in']): 
        return False
    if not link.startswith('http'): 
        link = urljoin(base_url, link)
    
    parsed_link = urlparse(link)# Parse the URL to get the domain
    base_domain = urlparse(base_url).netloc
    if parsed_link.netloc != base_domain and not parsed_link.netloc.endswith('.' + base_domain):
        return False
    return True


async def extract_contents_selenium(links, crawl_link):
    from bs4 import BeautifulSoup
    from logger import logger
    from selenium import webdriver
    try:
        logger.info("Inside extract_content_selenium")
        logger.info(f"links:{links}")

        response = []
        start_time = time.time()
        driver = webdriver.Chrome()

        def scrape_link(link):
            driver.get(link)
            time.sleep(3)
            parsed_content = BeautifulSoup(driver.page_source, 'html.parser')
            # logger.info(f"parsed_content: {parsed_content}")
            for tag in parsed_content.find_all(['header', 'footer', 'title']):
                tag.decompose()
            return extract_name_number_designation(parsed_content.get_text(separator=' ', strip=True))

        contact_links = [l for l in links if 'contact' in urlparse(l).path.lower()]
        other_links = [l for l in links if l not in contact_links]

        logger.info(f"Contact links found using selenium: {contact_links}")
        logger.info(f"Other links found using selenium: {other_links}")

        found_email = None
        found_number = None

        # Contact pages first; stop as soon as the pair is complete across pages.
        for link in contact_links:
            try:
                info = scrape_link(link)
                found_email = found_email or info.get('email')
                found_number = found_number or info.get('number')
                if info.get('email') or info.get('number'):
                    response.append({"link": link, **info})
                if found_email and found_number:
                    logger.info("Both email and number found, stopping.")
                    driver.quit()
                    return response
            except Exception as e:
                logger.error(f"An error occurred for link: {link}: {str(e)}")
                continue

        # If contact pages did not complete the pair, inspect at most 15 others.
        for link in other_links[:15]:
            try:
                info = scrape_link(link)
                found_email = found_email or info.get('email')
                found_number = found_number or info.get('number')
                if info.get('email') or info.get('number'):
                    response.append({"link": link, **info})
                if found_email and found_number:
                    logger.info("Both email and number found, stopping.")
                    break
            except Exception as e:
                logger.error(f"An error occurred for link: {link}: {str(e)}")
                continue

        driver.quit()
        total_time = process_tat(start_time, time.time())
        logger.info(f"Total time taken: {total_time}")
        logger.info(f"selenium metrics: {response}")
        return response

    except Exception as e:
        logger.error(f"An error occurred while crawling raw text website: {str(e)}")
        return {"status": 0, "message": "Unable to process text", "result": str(e)}