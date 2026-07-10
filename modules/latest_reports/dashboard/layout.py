from dash import html, dcc
import dash_leaflet as dl

def create_latest_reports_layout():
    return html.Div(
        className="pipac-section",
        children=[
            html.H2("Últimas Denuncias Nacionales", className="pipac-section-title"),
            html.Div(
                className="pipac-filter-stack horizontal",
                children=[
                    html.Label("Departamento:"),
                    dcc.Dropdown(id='lr-dept-filter', placeholder='Todos', className='pipac-dropdown'),
                    html.Label("Municipio:"),
                    dcc.Dropdown(id='lr-mpio-filter', placeholder='Todos', className='pipac-dropdown'),
                ]
            ),
            html.Div(
                className="pipac-kpi-grid",
                children=[
                    html.Div(className="pipac-card", children=[
                        html.H4("Total Denuncias"),
                        html.Div(id='lr-kpi-total', className="pipac-kpi-value", children="0")
                    ]),
                    html.Div(className="pipac-card", children=[
                        html.H4("Hoy"),
                        html.Div(id='lr-kpi-hoy', className="pipac-kpi-value", children="0")
                    ]),
                ]
            ),
            html.Div(
                className="pipac-map-shell",
                style={"height": "600px", "marginTop": "20px"},
                children=[
                    dl.Map(
                        id="lr-map",
                        center=[4.5709, -74.2973],
                        zoom=5,
                        children=[
                            dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"),
                            dl.LayerGroup(id="lr-map-markers")
                        ],
                        style={'width': '100%', 'height': '100%'}
                    )
                ]
            ),
            
            # Chatbot Section
            html.Div(
                className="pipac-card",
                style={"marginTop": "20px"},
                children=[
                    html.H3("Asistente de Inteligencia Artificial", style={"color": "#fff"}),
                    html.Div(
                        id="chatbot-history",
                        style={
                            "height": "300px", 
                            "overflowY": "auto", 
                            "backgroundColor": "#08111F", 
                            "padding": "10px", 
                            "borderRadius": "8px",
                            "border": "1px solid #1D2A42",
                            "marginBottom": "10px",
                            "color": "#F8FAFC"
                        }
                    ),
                    html.Div(
                        style={"display": "flex", "gap": "10px"},
                        children=[
                            dcc.Input(
                                id="chatbot-input",
                                type="text",
                                placeholder="Hazme una pregunta sobre criminalidad o riesgo...",
                                style={"flex": 1, "padding": "10px", "borderRadius": "4px", "backgroundColor": "#101C2E", "color": "#fff", "border": "1px solid #1D2A42"}
                            ),
                            html.Button("Enviar", id="chatbot-send-btn", n_clicks=0, className="pipac-primary-button", style={"padding": "10px 20px"})
                        ]
                    )
                ]
            )
        ]
    )
