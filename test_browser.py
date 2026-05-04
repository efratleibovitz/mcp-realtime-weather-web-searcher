# import asyncio
# from playwright.async_api import async_playwright

# async def test():
#     print("מתחיל בדיקה...")
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False) # יפתח דפדפן נראה לעין
#         page = await browser.new_page()
#         print("מנווט לאתר...")
#         await page.goto("https://www.weather2day.co.il/forecast")
#         await page.fill("input#forecast-search", "ירושלים")
#         print("הקלדתי ירושלים!")
#         await asyncio.sleep(5) # משאיר את הדפדפן פתוח ל-5 שניות שתראי
#         await browser.close()
#     print("בדיקה הסתיימה בהצלחה!")

# asyncio.run(test())

import asyncio
from playwright.async_api import async_playwright

async def run_full_weather_check():
    city_to_search = "ירושלים" # את יכולה לשנות לכל עיר
    
    print(f"--- מתחיל בדיקה אוטומטית מלאה עבור {city_to_search} ---")
    
    async with async_playwright() as p:
        # פתיחת דפדפן (headless=False כדי שתראי)
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("1. מנווט לאתר Weather2Day...")
        await page.goto("https://www.weather2day.co.il/forecast")
        
        # שלב 2: הזנת העיר
        print(f"2. מקליד '{city_to_search}' בשדה החיפוש...")
        search_input = "#city_search_forecast"
        await page.wait_for_selector(search_input)
        
        # במקום fill, נשתמש ב-click ואז type כדי שהאתר יזהה פעילות
        await page.click(search_input)
        # הקלדה עם השהיה קטנה בין אות לאות (כמו בן אדם)
        await page.type(search_input, city_to_search, delay=100)
        
        
        # שלב 3: בחירת העיר מהרשימה
       # שלב 3: בחירת העיר
        print("3. מחכה לרשימה הנפתחת...")
        # ננסה סלקטור רחב יותר לגיבוי
        suggestion_selector = "li.autocomplete-suggestion, .autocomplete-suggestion"
        
     # --- שלב 3: בחירת העיר ---
        print("3. מנסה לבחור את העיר...")
        suggestion_selector = ".autocomplete-suggestion"
        
        try:
            # מחכים קצת שהרשימה תצוף
            await page.wait_for_selector(suggestion_selector, timeout=5000)
            print("הרשימה הופיעה, לוחץ על האפשרות הראשונה...")
            await page.click(suggestion_selector)
        except:
            print("הרשימה לא הופיעה כאלמנט לחיץ, מנסה ניווט מקלדת...")
            # טריק: חץ למטה ואז אנטר
            await page.keyboard.press("ArrowDown")
            await asyncio.sleep(0.5)
            await page.keyboard.press("Enter")

        # --- שלב 4: חילוץ נתונים חכם ---
        # --- שלב 4: חילוץ נתונים חכם ---
       # --- שלב 4: חילוץ מרשימת סלקטורים ---
        print("4. מחלץ נתונים מרשימת סלקטורים...")

        # רשימת הסלקטורים שזיהינו כרלוונטיים (את יכולה להוסיף כאן עוד מה-Inspect)
        selectors_to_try = [
            ".temperature.green",  
            "div[data-color]",                # הטמפרטורה המרכזית
            ".current-weather .temperature",            # גרסה חלופית
            ".time",                    # עוד אפשרות נפוצה
            ".weather-detail",                # לפעמים זה ID
        ]

        weather_data = "לא נמצא נתון"
        
        for selector in selectors_to_try:
            try:
                # מחכים שהסלקטור יופיע
                element = await page.wait_for_selector(selector, timeout=2000)
                if element:
                    # חילוץ הטקסט
                    raw_text = await element.inner_text()
                    clean_text = raw_text.strip().replace('\n', ' ')
                    
                    # בדיקה אם יש שם מספר (כדי לוודא שזו טמפרטורה)
                    if any(char.isdigit() for char in clean_text):
                        # כאן השדרוג - אנחנו מדפיסים גם את הסלקטור וגם את הטקסט שלו!
                        print(f"✅ מצאתי בסלקטור [{selector}]:")
                        print(f"   >>> התוכן הוא: {clean_text}") # זה ידפיס לך למשל: 12.4°
                        
                        weather_data = clean_text
                        break 
            except:
                continue
       
        # --- סיום התהליך ---
        print("סוגר את הדפדפן...")
        await asyncio.sleep(3) 
        await browser.close()
        
    print("--- הבדיקה הסתיימה ---")

# הרצת התהליך
if __name__ == "__main__":
    asyncio.run(run_full_weather_check())