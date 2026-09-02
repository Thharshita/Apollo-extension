SIMILARITY_RESPONSE={"project_name":"application_name","content_id":"element_id","main_link":"link","sub_link":"internal_link","score":"match_score","project_id":"application_id","similar_content":"matching_content", "page_number":"page_count","file_type":"document","search_type":"metric_type"}

ips=['116.199.169.1:4145', '103.47.93.250:1080','103.205.128.41:4145', '103.47.93.232:1080	']

SUPPORTED_FILE_TYPES = [
    "docx", "docs", "pdf", "xps", "epub", "mobi", "fb2", "cbz", "svg", "pptx",
    "txt", "png", "jpeg", "png", "gif", "jpg", "bmp", "tiff"
]

PROXY= {
            "http": 'http://114.121.248.251:8080',
            "http_1": 'http://222.85.190.32:8090',
            "http_2": 'http://47.107.128.69:888',
            "http_3": 'http://41.65.146.38:8080',
            "http_4": 'http://190.63.184.11:8080',
            "http_5": 'http://45.7.135.34:999',
            "http_6": 'http://141.94.104.25:8080',
            "http_7": 'http://222.74.202.229:8080',
            "http_8": 'http://141.94.106.43:8080',
            "http_9": 'http://191.101.39.96:80'
        }

UNWANTED_DOMAINS =['linkedin.com','.pdf','.zip', 'xlsx','.jpg','twitter.com', 'facebook.com', 
            'youtube.com','play.google.com','instagram.com','dlai.in', '.mp4']

UNWANTED_PREFIXES = ['#', 'javascript:', 'mailto:', 'tel:']
UNWANTED_URLS = ['maps.app.goo.gl', 'google.com/maps']


PHONE_COL="Corporate Phone"
EMAIL_COL="Email"
COMPANY_WEBSITE_COL="Website"
COMPANY_NAME_COL="Company Name"
