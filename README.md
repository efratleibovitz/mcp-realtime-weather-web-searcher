# 🌍 MCP Real-Time Web Investigator
**An advanced Model Context Protocol (MCP) server for live data extraction and web automation.**

![MCP](https://img.shields.io/badge/MCP-Protocol-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen)
![Playwright](https://img.shields.io/badge/Powered%20by-Playwright-orange)

## 🎯 Overview
This project empowers AI Agents (like Claude Desktop or Custom GPTs) to break the "knowledge cutoff" barrier. Instead of relying on old training data, the Agent can physically "open a browser", navigate to websites, and extract real-time information.

Currently optimized for **Israel Weather Services**, but architected to scale for any real-time web investigation.

---

## 🚀 Key Features
* **Live Browser Interaction**: Uses Playwright to simulate human-like browsing.
* **Smart Selector Logic**: Robust extraction that tries multiple CSS selectors to find data.
* **Human-Mimic Typing**: Bypasses basic bot detection with delayed keystrokes.
* **Seamless MCP Integration**: Ready to plug into any MCP-compatible environment.

---

## 🛠 Installation & Setup

### Prerequisites
* Python 3.10+
* [Playwright](https://playwright.dev/python/docs/intro)

### Quick Start
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/mcp-realtime-web-searcher.git](https://github.com/YOUR_USERNAME/mcp-realtime-web-searcher.git)
   cd mcp-realtime-web-searcher

2. **Set up virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
      # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

4.  **Run the server:**
    ```bash
    python main.py
    ```

## 🤖 Usage: What can the Agent answer?
**✅ Currently Supported (Live Now)**
The Agent can handle complex, multi-step tasks like:

* "מה מזג האוויר כרגע בירושלים? תפתח דפדפן ותבדוק ב-Weather2Day."

* "תבדוק אם חם עכשיו בתל אביב ותגיד לי מה הטמפרטורה המדויקת."

## 🔮 Future Roadmap (Coming Soon)
With minor configuration, this Agent will support:

* **US Weather Hubs:** Real-time stats from NOAA and AccuWeather.

* **Stock Market:** Fetching live stock prices from financial portals.

* **Flight Tracking:** Checking if a flight is on time by scraping     airport boards.

## 🏗 Architecture
The server exposes 4 main tools:

1.open_weather_forecast_israel: Launches the session.

2.enter_weather_forecast_city_israel: Handles search input.

3.select_weather_forecast_city_israel: Manages dropdown selection.

4.get_weather_data_from_page: The "brain" that extracts the clean data.

## 🤝 Contributing
Found a bug or want to add a new site? Feel free to open a Pull Request!

**Author:** [Efrat Leibovitz]

Turning static LLMs into dynamic Web Agents.