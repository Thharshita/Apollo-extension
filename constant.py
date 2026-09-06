import os


SIMILARITY_RESPONSE={"project_name":"application_name","content_id":"element_id","main_link":"link","sub_link":"internal_link","score":"match_score","project_id":"application_id","similar_content":"matching_content", "page_number":"page_count","file_type":"document","search_type":"metric_type"}

ips=['116.199.169.1:4145', '103.47.93.250:1080','103.205.128.41:4145', '103.47.93.232:1080	']

SUPPORTED_FILE_TYPES = [
    "docx", "docs", "pdf", "xps", "epub", "mobi", "fb2", "cbz", "svg", "pptx",
    "txt", "png", "jpeg", "png", "gif", "jpg", "bmp", "tiff"
]

PROXY_URL = os.getenv("SCRAPER_PROXY_URL")
PROXY = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else {}

UNWANTED_DOMAINS =['linkedin.com','.pdf','.zip', 'xlsx','.jpg','twitter.com', 'facebook.com', 
            'youtube.com','play.google.com','instagram.com','dlai.in', '.mp4']

UNWANTED_PREFIXES = ['#', 'javascript:', 'mailto:', 'tel:']
UNWANTED_URLS = ['maps.app.goo.gl', 'google.com/maps']


PHONE_COL="Corporate Phone"
EMAIL_COL="Email"
COMPANY_WEBSITE_COL="Website"
COMPANY_NAME_COL="Company Name"
