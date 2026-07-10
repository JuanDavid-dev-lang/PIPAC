import httpx
from dash import Input, Output, State, html
from dashboard.app import app

# API URL for Chatbot
CHATBOT_API_URL = "http://127.0.0.1:8000/api/v1/latest-reports/chat"

@app.callback(
    Output("chatbot-history", "children"),
    Input("chatbot-send-btn", "n_clicks"),
    State("chatbot-input", "value"),
    State("chatbot-history", "children"),
    prevent_initial_call=True
)
def update_chatbot(n_clicks, user_message, history):
    if not user_message:
        return history
        
    history = history or []
    
    # Add User Message to History
    user_bubble = html.Div(
        style={"display": "flex", "justifyContent": "flex-end", "marginBottom": "10px"},
        children=[
            html.Div(
                style={"backgroundColor": "#3B82F6", "padding": "10px 15px", "borderRadius": "15px 15px 0 15px", "maxWidth": "75%"},
                children=user_message
            )
        ]
    )
    
    history.append(user_bubble)
    
    # Send Request to API
    try:
        # Note: In a real dash app, we might use requests or an internal call if on same server.
        # Since this is run alongside FastAPI, we use requests to the API endpoint.
        import requests
        resp = requests.post(CHATBOT_API_URL, json={"message": user_message}, timeout=10)
        
        if resp.status_code == 200:
            bot_reply = resp.json().get("response", "Lo siento, hubo un error procesando tu respuesta.")
        else:
            bot_reply = "Hubo un problema de conexión con el Asistente Predictivo."
            
    except Exception as e:
        bot_reply = f"Error conectando con el modelo de IA: {str(e)}"
        
    # Add Bot Message to History
    bot_bubble = html.Div(
        style={"display": "flex", "justifyContent": "flex-start", "marginBottom": "10px"},
        children=[
            html.Div(
                style={"backgroundColor": "#1D2A42", "padding": "10px 15px", "borderRadius": "15px 15px 15px 0", "maxWidth": "75%"},
                children=bot_reply
            )
        ]
    )
    
    history.append(bot_bubble)
    
    return history
