from scrapers.web_scraper_bs import fetch_links, extract_contents
from logger import logger
from fastapi import Query,APIRouter, Depends, UploadFile, File
import validators
from fastapi.responses import JSONResponse
import pandas as pd
import io
from constant import PHONE_COL, EMAIL_COL, COMPANY_NAME_COL, COMPANY_WEBSITE_COL
from scrapers.google_scraper import duckduckgo_search
import asyncio

router=APIRouter(tags=["SCRAPE"])

@router.get("/duckduckgo-search/")
async def duckduckgo_search_data(
    query: str = Query(..., min_length=1, description="Company name or search query"),
    max_results: int = Query(10, ge=1, le=50, description="Number of results to return"),
) -> dict:
    try:
        query = query.strip()
        if not query:
            return JSONResponse(status_code=400, content={"message": "Query cannot be empty"})

        results = await asyncio.to_thread(duckduckgo_search, query, max_results)
        return {"query": query, "count": len(results), "results": results}
    except Exception as e:
        logger.error(f"DuckDuckGo search failed: {e}")
        return JSONResponse(status_code=502, content={"message": str(e)})

@router.post("/scrape-link/")
async def scrape_link_data(link:str)-> dict:
    try:
        if not validators.url(link):
            return JSONResponse(
                status_code=400,
                content={
                    "message": "Invalid URL",
                    "result": "Please provide the URL in the format https://moneyview.in/"
                }
            )
        
        if link.endswith("/"):
            link=link[:-1]           

        link_status, links, use_selenium = await fetch_links(link)  #array of link
        if link_status==0:
            return links
        
        response= await extract_contents(links, use_selenium,link)
        return {"response":response}
    
    except Exception as e:
        logger.info(f"An error occurred while scraping: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "message": str(e),
            }
        )

# @router.post("/process-excel")
# async def process_excel(file:UploadFile= File(...)):
#     if not file.filename.endswith((".xlsx",".xls")):
#         return JSONResponse(
#             status_code=400,
#             content={
#                 "message": "Invalid file format",
#                 "result": "Please upload an Excel file with the extension .xlsx"
#             }
#         )
#     content= await file.read()

#     try:
#         df= pd.read_excel(io.ByytesIO(content))
#     except Exception as e:
#         logger.info(f"An error occurred while reading the Excel file: {str(e)}")
#         return JSONResponse(
#             status_code=400,
#             content={
#                 "message": "Error reading Excel file",
#                 "result": str(e)
#             }
#         )

#     for col in (PHONE_COL, EMAIL_COL, COMPANY_WEBSITE_COL):
#         if col not in df.columns:
#             df[col] = None 

#     missing_input_cols= [c for c in [PHONE_COL, EMAIL_COL, COMPANY_WEBSITE_COL] if c not in df.columns]

#     if missing_input_cols:
#         return JSONResponse(
#             status_code=400,
#             content={
#                 "message": "Missing required columns",
#                 "result": f"Please ensure the Excel file contains the following columns: {missing_input_cols}"
#             }
#         )