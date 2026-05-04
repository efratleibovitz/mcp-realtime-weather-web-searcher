from mcp.server.fastmcp import FastMCP
from playwright.async_api import TimeoutError as PlaywrightTimeout
from playwright.async_api import async_playwright
import asyncio

mcp = FastMCP("Weather_Israel_Automation")
FORECAST_URL = "https://www.weather2day.co.il/forecast"

browser_context = {"browser": None, "page": None, "playwright": None}

state = {
    "playwright": None,
    "browser": None,
    "page": None
}

async def ensure_browser():
    """מוודא שהדפדפן פתוח ומוכן לעבודה"""
    if state["browser"] is None:
        state["playwright"] = await async_playwright().start()
        # headless=False מאפשר לראות את הפעולה בזמן אמת
        state["browser"] = await state["playwright"].chromium.launch(headless=False)
        state["page"] = await state["browser"].new_page()
    return state["page"]

@mcp.tool()
async def open_weather_forecast_israel() -> str:
    """Opens the browser and navigates to the Weather2Day forecast page."""
    page = await ensure_browser()
    await page.goto(FORECAST_URL)
    return "The weather website is now open."

# --- Tool 2: הזנת שם עיר ---
@mcp.tool()
async def enter_weather_forecast_city_israel(city_name: str) -> str:
    """
    Step 2: Enters the city name into the search field using human-like typing.
    """
    page = await ensure_browser()
    search_input = "#city_search_forecast" # הסלקטור מהטסט המוצלח שלך
    
    await page.wait_for_selector(search_input)
    await page.click(search_input)
    # הקלדה עם השהיה קטנה כדי שהאתר יקפיץ את הרשימה
    await page.type(search_input, city_name, delay=100)
    
    return f"Entered city '{city_name}' into the search field. Waiting for suggestions..."
# --- Tool 3: בחירת העיר מהרשימה ---
@mcp.tool()
async def select_weather_forecast_city_israel() -> str:
    """
    Step 3: Selects the city from the dropdown or using keyboard if needed.
    """
    page = await ensure_browser()
    suggestion_selector = ".autocomplete-suggestion"
    
    try:
        # ניסיון לחיצה על ההצעה הראשונה
        await page.wait_for_selector(suggestion_selector, timeout=5000)
        await page.click(suggestion_selector)
        await page.wait_for_load_state("networkidle")
        return "Successfully selected the city from the list."
    except Exception:
        # גיבוי - ניווט מקלדת כמו בטסט
        await page.keyboard.press("ArrowDown")
        await asyncio.sleep(0.5)
        await page.keyboard.press("Enter")
        await page.wait_for_load_state("networkidle")
        return "City selected using keyboard navigation."
    
@mcp.tool()
async def get_weather_data_from_page() -> str:
    """
    Step 4: Smartly extracts the actual temperature and weather data using multiple selectors.
    """
    page = await ensure_browser()
    
    # רשימת הסלקטורים מהטסט המוצלח שלך
    selectors_to_try = [
        ".temperature.green",  
        "div[data-color]", 
        ".current-weather .temperature",
        ".time",
        ".weather-detail"
    ]

    found_data = []

    for selector in selectors_to_try:
        try:
            # מחפשים כל סלקטור לזמן קצר
            element = await page.wait_for_selector(selector, timeout=2000)
            if element:
                raw_text = await element.inner_text()
                clean_text = raw_text.strip().replace('\n', ' ')
                
                # בדיקה אם הטקסט מכיל ספרות (לוודא שזו טמפרטורה/נתון רלוונטי)
                if any(char.isdigit() for char in clean_text):
                    found_data.append(clean_text)
                    # אם מצאנו נתון מרכזי אחד, אפשר לעצור או להמשיך לאסוף
                    break 
        except:
            continue

    if found_data:
        return f"Weather data extracted: {', '.join(found_data)}"
    else:
        # מוצא אחרון - חילוץ טקסט כללי מהחלק העליון
        try:
            content = await page.evaluate("document.body.innerText")
            return f"Could not find specific elements. Raw snippet: {content[:300]}"
        except Exception as e:
            return f"Error extracting data: {str(e)}"

# def main():
#     mcp.run(transport="stdio")


# if __name__ == "__main__":
#     main()

if __name__ == "__main__":
    mcp.run()