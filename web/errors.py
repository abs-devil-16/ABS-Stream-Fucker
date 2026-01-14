from fastapi.responses import HTMLResponse

def error_page(error_type: str, message: str) -> HTMLResponse:
    """Generate error page HTML"""
    
    error_messages = {
        "invalid_token": {
            "title": "Invalid Link BC! 🚫",
            "emoji": "❌",
            "message": "Ye link invalid hai chutiye!",
            "details": "Link galat hai, delete ho gaya, ya expire ho gaya."
        },
        "invalid_key": {
            "title": "Invalid Key MC! 🔐",
            "emoji": "⚠️",
            "message": "Security key galat hai bhenchod!",
            "details": "Key verify nahi ho rahi. Link dhang se copy kiya?"
        },
        "expired": {
            "title": "Link Expired! ⏰",
            "emoji": "⏰",
            "message": "Arre yaar, link expire ho gaya!",
            "details": "Free user ka link tha, ab khatam ho gaya. Owner se naya maang!"
        },
        "file_not_found": {
            "title": "File Not Found! 📁",
            "emoji": "❌",
            "message": "File nahi mili BC!",
            "details": "File delete ho gayi ya koi technical issue hai."
        },
        "server_error": {
            "title": "Server Error! 💀",
            "emoji": "💀",
            "message": "Server ki maa chud gayi!",
            "details": "Thodi der me try kar. Ya owner ko bol."
        },
        "access_denied": {
            "title": "Access Denied! 🚫",
            "emoji": "🚫",
            "message": "Tereko access nahi hai MC!",
            "details": "Direct link open karne ki koshish ki? Nice try bhenchod!"
        }
    }
    
    error_info = error_messages.get(error_type, error_messages["server_error"])
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{error_info['title']}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            
            .error-container {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                max-width: 500px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                text-align: center;
                animation: slideIn 0.5s ease-out;
            }}
            
            @keyframes slideIn {{
                from {{
                    opacity: 0;
                    transform: translateY(-50px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .emoji {{
                font-size: 80px;
                margin-bottom: 20px;
                animation: bounce 1s infinite;
            }}
            
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-20px); }}
            }}
            
            h1 {{
                color: #333;
                font-size: 28px;
                margin-bottom: 15px;
            }}
            
            .message {{
                color: #e74c3c;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 15px;
            }}
            
            .details {{
                color: #666;
                font-size: 16px;
                line-height: 1.6;
                margin-bottom: 30px;
            }}
            
            .btn {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 40px;
                border-radius: 50px;
                text-decoration: none;
                font-size: 16px;
                font-weight: bold;
                transition: transform 0.3s ease;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }}
            
            .btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
            }}
            
            .footer {{
                margin-top: 30px;
                color: #999;
                font-size: 14px;
            }}
            
            @media (max-width: 600px) {{
                .error-container {{
                    padding: 30px 20px;
                }}
                
                h1 {{
                    font-size: 24px;
                }}
                
                .message {{
                    font-size: 18px;
                }}
                
                .emoji {{
                    font-size: 60px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="error-container">
            <div class="emoji">{error_info['emoji']}</div>
            <h1>{error_info['title']}</h1>
            <p class="message">{error_info['message']}</p>
            <p class="details">{error_info['details']}</p>
            <a href="https://t.me/ABSStreamFuckerBot" class="btn">🤖 Go to Bot</a>
            <div class="footer">
                <p>ABS-Stream-Fucker © 2024</p>
                <p>Made with 💀 and gaali</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html, status_code=403)
