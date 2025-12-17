#!/usr/bin/env python3
"""
Box 3 Browser Automation MCP Wrapper
Uses Olmo-3-7B-Think for Playwright script generation + execution
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional

import requests
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Box3 Browser MCP", version="1.0.0")

# Ollama configuration
OLLAMA_HOST = "http://localhost:11434"
OLMO_MODEL = "olmo-3-7b-think"

# Playwright browser instance (singleton)
BROWSER = None
CONTEXT = None


# =============================================================================
# REQUEST MODELS
# =============================================================================

class BrowserAutomateRequest(BaseModel):
    """Browser automation task request"""
    task_description: str
    url: Optional[str] = None
    execute: bool = True  # If False, just generate script
    headless: bool = True


class BrowserExecuteRequest(BaseModel):
    """Execute pre-generated Playwright script"""
    script: str
    headless: bool = True


class AmazonListingRequest(BaseModel):
    """Create Amazon listing automation"""
    product_title: str
    product_description: str
    price: float
    images: List[str]
    category: str
    keywords: List[str]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def ollama_generate_playwright(task: str) -> str:
    """Generate Playwright script using Olmo"""
    url = f"{OLLAMA_HOST}/api/generate"
    
    prompt = f"""You are a Playwright automation expert. Generate a Python async function using Playwright to accomplish this task:

Task: {task}

Requirements:
1. Use async/await syntax
2. Include error handling
3. Add comments for clarity
4. Return extracted data if applicable
5. Use proper selectors (prefer data-testid, then id, then CSS)

Generate only the Python code, no explanations:

```python
async def automate_task(page):
    # Your code here
    pass
```
"""
    
    payload = {
        "model": OLMO_MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.3  # Lower temp for code generation
    }
    
    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    
    result = response.json()
    return result.get("response", "")


async def execute_playwright_script(script: str, headless: bool = True) -> Dict:
    """Execute Playwright script safely"""
    global BROWSER, CONTEXT
    
    # Initialize browser if needed
    if BROWSER is None:
        playwright = await async_playwright().start()
        BROWSER = await playwright.chromium.launch(headless=headless)
        CONTEXT = await BROWSER.new_context()
    
    page = await CONTEXT.new_page()
    
    try:
        # Extract function from script
        # Execute it
        local_scope = {"page": page}
        exec(script, local_scope)
        
        # Call the function if it exists
        if "automate_task" in local_scope:
            result = await local_scope["automate_task"](page)
            return {"success": True, "result": result}
        else:
            return {"success": False, "error": "Function 'automate_task' not found in script"}
    
    except Exception as e:
        logger.error(f"Script execution error: {e}")
        return {"success": False, "error": str(e)}
    
    finally:
        await page.close()


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": OLMO_MODEL,
        "browser_ready": BROWSER is not None
    }


@app.post("/browser/automate")
async def browser_automate(request: BrowserAutomateRequest):
    """
    Generate and optionally execute Playwright automation
    
    Use case: "Navigate to Amazon and search for leather wallets"
    Workflow:
    1. Olmo generates Playwright script
    2. Optionally execute script
    3. Return results
    """
    start_time = time.time()
    
    try:
        # Generate script
        logger.info(f"Generating Playwright script for: {request.task_description}")
        script = ollama_generate_playwright(request.task_description)
        
        generation_time = time.time() - start_time
        
        # Execute if requested
        execution_result = None
        if request.execute:
            logger.info("Executing generated script")
            execution_result = await execute_playwright_script(script, request.headless)
        
        total_time = time.time() - start_time
        
        return {
            "success": True,
            "script": script,
            "generation_time": generation_time,
            "execution_result": execution_result,
            "total_time": total_time
        }
    
    except Exception as e:
        logger.error(f"Automation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/browser/execute")
async def browser_execute(request: BrowserExecuteRequest):
    """
    Execute pre-generated Playwright script
    
    Use case: Re-run previously generated automation
    """
    try:
        result = await execute_playwright_script(request.script, request.headless)
        return result
    
    except Exception as e:
        logger.error(f"Execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/browser/amazon_listing")
async def create_amazon_listing(request: AmazonListingRequest):
    """
    Automated Amazon listing creation
    
    Use case: Phase 2 - Create listings from supplier products
    Workflow:
    1. Generate Playwright script for Amazon Seller Central
    2. Fill product form (title, description, price, images)
    3. Submit listing
    """
    try:
        # Build task description
        task = f"""
Navigate to Amazon Seller Central and create a new product listing:

Product Details:
- Title: {request.product_title}
- Description: {request.product_description}
- Price: ${request.price}
- Category: {request.category}
- Keywords: {', '.join(request.keywords)}
- Images: {len(request.images)} images to upload

Steps:
1. Log in to Amazon Seller Central (assume credentials are saved)
2. Navigate to "Add a Product"
3. Search for product category: {request.category}
4. Fill all required fields
5. Upload images from URLs: {', '.join(request.images[:3])}
6. Set price to ${request.price}
7. Review and submit (but do NOT click final submit - stop at preview)
8. Return the listing preview URL
"""
        
        # Generate and execute
        script = ollama_generate_playwright(task)
        result = await execute_playwright_script(script, headless=False)  # Show browser for verification
        
        return {
            "success": True,
            "script": script,
            "result": result,
            "product_title": request.product_title
        }
    
    except Exception as e:
        logger.error(f"Amazon listing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/browser/scrape")
async def browser_scrape(url: str, selector: str):
    """
    Simple scraping endpoint
    
    Use case: Extract data from web pages
    """
    try:
        global BROWSER, CONTEXT
        
        if BROWSER is None:
            playwright = await async_playwright().start()
            BROWSER = await playwright.chromium.launch(headless=True)
            CONTEXT = await BROWSER.new_context()
        
        page = await CONTEXT.new_page()
        await page.goto(url)
        
        # Extract data
        elements = await page.query_selector_all(selector)
        data = [await el.text_content() for el in elements]
        
        await page.close()
        
        return {
            "success": True,
            "url": url,
            "selector": selector,
            "data": data,
            "count": len(data)
        }
    
    except Exception as e:
        logger.error(f"Scrape error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/browser/close")
async def close_browser():
    """Close browser instance"""
    global BROWSER, CONTEXT
    
    if BROWSER:
        await BROWSER.close()
        BROWSER = None
        CONTEXT = None
    
    return {"success": True, "message": "Browser closed"}


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Box 3 Browser MCP Wrapper on port 8085")
    uvicorn.run(app, host="0.0.0.0", port=8085)
