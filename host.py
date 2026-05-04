# import asyncio
# from contextlib import AsyncExitStack
# from typing import Any
# import os
# from groq  import Groq
# import httpx
# import json
# from anthropic import Anthropic
# from client import MCPClient
# from dotenv import load_dotenv
# import google.generativeai as genai
# from google.generativeai.types import content_types
# load_dotenv()


# class ChatHost:
#     def __init__(self):
#         self.mcp_clients: list[MCPClient] = [MCPClient("./weather_USA.py")]
#         # self.tool_clients: dict[str, tuple[MCPClient, str]] = {}
#         self.clients_connected = False
#         self.exit_stack = AsyncExitStack()
#         genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
#         transport = httpx.HTTPTransport(verify=False)
#         # self.groq_client = Groq(
#         # api_key=os.environ.get("GROQ_API_KEY"),
#         # http_client=httpx.Client(transport=transport)
#         # )
#         self.model = genai.GenerativeModel(
#             model_name="gemini-1.5-flash",
#         )
#     async def connect_mcp_clients(self):
#         """Connect all configured MCP clients once."""
#         if self.clients_connected:
#             return

#         for client in self.mcp_clients:
#             if client.session is None:
#                 await client.connect_to_server()

#         if not self.mcp_clients:
#             raise RuntimeError("No MCP clients are connected")

#         self.clients_connected = True
   
#     async def get_tools_for_gemini(self):
#         """המרת כלי ה-MCP לפורמט ש-Gemini מבין"""
#         await self.connect_mcp_clients()
#         gemini_tools = []
#         self.tool_map = {} # למיפוי חוזר ל-MCP

#         for client in self.mcp_clients:
#             response = await client.session.list_tools()
#             for tool in response.tools:
#                 # Gemini יכול לקבל פונקציות ישירות, אבל ב-MCP אנחנו צריכים תיווך
#                 # נבנה הגדרה שתואמת למבנה של Gemini
#                 tool_def = {
#                     "name": f"{client.client_name}__{tool.name}",
#                     "description": tool.description,
#                     "parameters": tool.inputSchema
#                 }
#                 gemini_tools.append(tool_def)
#                 self.tool_map[tool_def["name"]] = (client, tool.name)
        
#         return gemini_tools
#     # async def get_available_tools(self) -> list[dict[str, Any]]:
#     #     """Collect tools from all MCP clients and map them back to their owner."""
#     #     await self.connect_mcp_clients()
#     #     self.tool_clients = {}
#     #     available_tools: list[dict[str, Any]] = []

#     #     for client in self.mcp_clients:
#     #         if client.session is None:
#     #             print(f"Warning: MCP client {client.client_name} is not connected, skipping")
#     #             continue

#     #         try:
#     #             response = await client.session.list_tools()
#     #             for tool in response.tools:
#     #                 exposed_name = f"{client.client_name}__{tool.name}"
#     #                 if exposed_name in self.tool_clients:
#     #                     raise RuntimeError(f"Duplicate tool name detected: {exposed_name}")

#     #                 self.tool_clients[exposed_name] = (client, tool.name)
#     #                 # בתוך get_available_tools:
#     #                 available_tools.append({
#     #                     "type": "function", 
#     #                     "function": {
#     #                         "name": exposed_name,
#     #                         "description": f"[{client.client_name}] {tool.description}",
#     #                         "parameters": tool.inputSchema, # שינוי שם המפתח ל-parameters
#     #                     }
#     #                 })
#     #         except Exception as e:
#     #             print(f"Warning: Failed to get tools from {client.client_name}: {str(e)}")
#     #             continue

#     #     if not available_tools:
#     #         raise RuntimeError("No tools available from any MCP client")

#     #     return available_tools


  

#     async def process_query(self, query: str) -> str:
#         """Process a query using Groq and available tools"""
#         # 1. אתחול רשימת ההודעות
#         messages = [{"role": "user", "content": query}]
#         available_tools = await self.get_available_tools()
#         final_text = []

#         while True:
#             # 2. קריאה ל-API של Groq
#             response = self.groq_client.chat.completions.create(
#                 model="llama3-70b-8192",
#                 messages=messages,
#                 tools=available_tools,
#                 tool_choice="auto",
#                 max_tokens=1000
#             )

#             # 3. חילוץ הודעת ה-Assistant
#             response_message = response.choices[0].message
#             messages.append(response_message) # חובה להוסיף להיסטוריה

#             # אם המודל החזיר טקסט רגיל, נוסיף אותו לתוצאה הסופית
#             if response_message.content:
#                 final_text.append(response_message.content)

#             # 4. בדיקה האם המודל רוצה להשתמש בכלים
#             if not response_message.tool_calls:
#                 # אם אין קריאות לכלים - סיימנו את הלולאה
#                 break

#             # 5. עיבוד הקריאות לכלים (יכולות להיות כמה במקביל)
#             for tool_call in response_message.tool_calls:
#                 tool_name = tool_call.function.name
                
#                 # Groq מחזיר את הארגומנטים כסטרינג של JSON, צריך להמיר לדיקט
#                 tool_args = json.loads(tool_call.function.arguments)

#                 if tool_name not in self.tool_clients:
#                     raise RuntimeError(f"Unknown tool requested: {tool_name}")

#                 # איתור הלקוח והפעלת הכלי
#                 client, original_tool_name = self.tool_clients[tool_name]
#                 if client.session is None:
#                     raise RuntimeError(f"MCP client {client.client_name} is not connected")

#                 # קריאה לכלי דרך ה-MCP Client
#                 result = await client.session.call_tool(original_tool_name, tool_args)
                
#                 final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

#                 # 6. הוספת תוצאת הכלי לרשימת ההודעות (חובה בפורמט הזה עבור Groq/OpenAI)
#                 messages.append({
#                     "role": "tool",
#                     "tool_call_id": tool_call.id, # המזהה הייחודי שהמודל נתן לקריאה
#                     "name": tool_name,
#                     "content": str(result.content),
#                 })

#     # מחזיר את כל מה שנאסף במהלך הריצה
#         return "\n".join(final_text)

#     async def chat_loop(self):
#         """Run an interactive chat loop"""
#         print("\nMCP Client Started!")
#         print("Type your queries or 'quit' to exit.")
        
#         while True:
#             try:
#                 query = input("\nQuery: ").strip()
                
#                 if query.lower() == 'quit':
#                     break
                
#                 response = await self.process_query(query)
#                 print("\n" + response)
                
#             except Exception as e:
#                 print(f"\nchat_loop Error: {str(e)}")
                
#     async def cleanup(self):
#         """Clean up resources"""
#         for client in reversed(self.mcp_clients):
#             await client.cleanup()
#         await self.exit_stack.aclose()
        
        
# async def main():
#     host = ChatHost()
#     try:
#         await host.chat_loop()
#     finally:
#         await host.cleanup()
        
# if __name__ == "__main__":
#     asyncio.run(main())
import os
import ssl

# 1. פקודה שמשתיקה את כל אזהרות ה-SSL של פייתון
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''

# 2. דריסת פונקציית ברירת המחדל של אימות SSL
ssl._create_default_https_context = ssl._create_unverified_context

import asyncio
import warnings
# השתקת האזהרות שיופיעו בטרמינל (כדי שיהיה לך נקי בעיניים)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

from google import genai
from google.genai import types
from client import MCPClient
from dotenv import load_dotenv

load_dotenv()
class ChatHost:
    
    def __init__(self):
        self.mcp_clients: list[MCPClient] = [MCPClient("./weather_USA.py"),MCPClient("./weather_Israel.py")]
        self.clients_connected = False
        
        # הגדרה פשוטה - העקיפה מתבצעת דרך משתני הסביבה שהוספנו למעלה
        self.client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
            http_options={
                'api_version': 'v1alpha', # לפעמים עוזר בגרסאות פלאש 2.0
            }
        )
        self.model_id = "gemini-2.0-flash"

    async def connect_mcp_clients(self):
        if self.clients_connected: return
        for client in self.mcp_clients:
            if client.session is None: await client.connect_to_server()
        self.clients_connected = True

    def clean_schema(self, schema):
        """ניקוי השדות שגורמים לשגיאה בג'מיני"""
        if isinstance(schema, dict):
            # הסרת שדות שלא נתמכים ב-Gemini Tool Schema
            schema.pop('title', None)
            schema.pop('additionalProperties', None)
            for key, value in schema.items():
                self.clean_schema(value)
        elif isinstance(schema, list):
            for item in schema:
                self.clean_schema(item)
        return schema

    async def get_tools_for_gemini(self):
        await self.connect_mcp_clients()
        gemini_tools = []
        self.tool_map = {}

        for client in self.mcp_clients:
            response = await client.session.list_tools()
            for tool in response.tools:
                # ניקוי ה-Schema לפני השליחה לג'מיני
                cleaned_input_schema = self.clean_schema(tool.inputSchema)
                
                tool_def = types.FunctionDeclaration(
                    name=f"{client.client_name}__{tool.name}",
                    description=tool.description,
                    parameters=cleaned_input_schema
                )
                gemini_tools.append(types.Tool(function_declarations=[tool_def]))
                self.tool_map[tool_def.name] = (client, tool.name)
        
        return gemini_tools

    async def process_query(self, query: str) -> str:
        available_tools = await self.get_tools_for_gemini()
        
        # יצירת צ'אט עם תמיכה אוטומטית בכלים
        config = {"tools": available_tools}
        chat = self.client.chats.create(model=self.model_id, config=config)
        
        final_text = []
        # שליחת השאילתה - הספרייה החדשה מטפלת בלולאת הכלים אוטומטית!
        response = chat.send_message(query)
        
        # איסוף התשובות (כולל חיווי על קריאה לכלים)
        for part in response.candidates[0].content.parts:
            if part.text:
                final_text.append(part.text)
            if part.function_call:
                final_text.append(f"[מפעיל כלי: {part.function_call.name}]")
                
        return "\n".join(final_text)

    async def chat_loop(self):
        print("\nסוכן Gemini 2.0 מוכן לעבודה!")
        while True:
            try:
                query = input("\nשאלה: ").strip()
                if query.lower() in ['quit', 'exit']: break
                res = await self.process_query(query)
                print(f"\n{res}")
            except Exception as e:
                print(f"\nשגיאה במערכת: {str(e)}")

    async def cleanup(self):
        for client in self.mcp_clients: await client.cleanup()

async def main():
    host = ChatHost()
    try: await host.chat_loop()
    finally: await host.cleanup()

if __name__ == "__main__":
    asyncio.run(main())