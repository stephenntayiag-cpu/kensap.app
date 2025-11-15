import os
import json
import dash
from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL

# -----------------------------
# File paths
# -----------------------------
USERS_FILE = "data/users.json"
ALUMNI_FILE = "data/alumni.json"
COMMENTS_FILE = "data/comments.txt"
PHOTOS_FOLDER = "static/photos"

# Ensure files exist
os.makedirs("data", exist_ok=True)
os.makedirs(PHOTOS_FOLDER, exist_ok=True)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(ALUMNI_FILE):
    with open(ALUMNI_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(COMMENTS_FILE):
    with open(COMMENTS_FILE, "w") as f:
        f.write("")

# -----------------------------
# Initialize app
# -----------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True)
app.title = "KenSAP"
server = app.server

# -----------------------------
# Helper functions for gallery
# -----------------------------
def get_comments(photo_name):
    comments_list = []
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, "r") as f:
            for line in f:
                if "|" in line:
                    fname, comment = line.strip().split("|", 1)
                    if fname == photo_name:
                        comments_list.append(comment)
    return comments_list

def save_comment(photo_name, comment):
    with open(COMMENTS_FILE, "a") as f:
        f.write(f"{photo_name}|{comment.strip()}\n")

# -----------------------------
# Login Layout
# -----------------------------
login_layout = html.Div([
    dbc.Container([
        html.H2("KenSAP Login", className="text-center", style={"marginTop": "50px"}),
        dbc.Row([
            dbc.Col([
                dbc.Input(id="username", placeholder="Username", type="text", style={"marginTop": "20px"}),
                dbc.Input(id="password", placeholder="Password", type="password", style={"marginTop": "10px"}),
                dbc.Button("Login", id="login-button", color="primary", style={"marginTop": "20px"}),
                dbc.Button("Sign Up", id="signup-button", color="secondary", style={"marginTop": "10px"}),
                html.Div(id="login-output", style={"marginTop": "20px", "color": "red"}),
            ], width=6)
        ], justify="center")
    ])
])

# -----------------------------
# Homepage Layout
# -----------------------------
homepage_layout = html.Div([
    dbc.Container([
        html.H1("Welcome to KenSAP", style={'textAlign': 'center', 'color': '#C0154B', 'marginTop': '30px'}),
        html.H4("Empowering Kenya’s Brightest Minds for Global Impact",
                style={'textAlign': 'center', 'color': '#555555', 'marginBottom': '20px'}),
        dcc.Link(
            dbc.Button("Learn More", color="primary", style={'display': 'block', 'margin': '0 auto', 'marginBottom': '40px'}),
            href="/gallery"
        )
    ]),

    dbc.Container([
        html.H2("About KenSAP", style={'color': '#C0154B', 'marginTop': '20px'}),
        html.P(
            "The Kenya Scholar Access Program (KenSAP) is a non-profit initiative that identifies, prepares, "
            "and connects exceptional Kenyan students from underprivileged backgrounds with educational opportunities "
            "at some of the world’s leading universities, primarily in North America. "
            "Since its founding in 2004, KenSAP has transformed the lives of hundreds of scholars.",
            style={'fontSize': '18px', 'lineHeight': '1.8'}
        ),
    ], style={'marginBottom': '40px'}),

    dbc.Container([
        html.H2("Our Impact", style={'color': '#C0154B', 'marginTop': '20px', 'textAlign': 'center'}),
        html.P(
            "Over 320 students helped to access top universities globally.\n"
            "Alumni active in leadership, research, and entrepreneurship.\n"
            "Annual fundraising and mentoring programs to sustain opportunities.",
            style={'fontSize': '16px', 'lineHeight': '1.8', 'textAlign': 'center'}
        )
    ], style={'marginBottom': '40px'}),
])
# -----------------------------
# Gallery Layout
# -----------------------------
photo_elements = []
for filename in os.listdir(PHOTOS_FOLDER):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        photo_elements.append(
            html.Div([
                html.Img(src=f"/{PHOTOS_FOLDER}/{filename}", style={"width": "300px", "margin": "10px 0"}),
                html.Div(id={'type': 'comments', 'index': filename}),
                dbc.Input(id={'type': 'input', 'index': filename}, placeholder="Add a comment...", type="text"),
                dbc.Button("Submit", id={'type': 'submit', 'index': filename}, color="primary", n_clicks=0, style={"marginTop": "5px"})
            ], style={"border": "1px solid #ccc", "padding": "10px", "marginBottom": "20px"})
        )

gallery_layout = html.Div([
    html.H2("Gallery", style={"textAlign": "center", "marginTop": "20px"}),
    html.Div(photo_elements)
])

# -----------------------------
# Alumni Layout
# -----------------------------
alumni_layout = html.Div([
    dbc.Container([
        html.H2("KenSAP Alumni", className="text-center", style={"marginTop": "30px"}),
        html.Hr(),
        html.Div(id="alumni-list", style={"marginTop": "20px"}),
        html.Hr(),
        html.Div([
            html.H4("Add Yourself to Alumni List:"),
            dbc.Input(id="alumni-name-input", placeholder="Enter your username", type="text", style={"marginTop": "10px"}),
            dbc.Button("Add Me", id="add-alumni-button", color="primary", style={"marginTop": "10px"}),
            html.Div(id="alumni-output", style={"marginTop": "15px", "color": "green"})
        ], style={"marginTop": "30px"})
    ])
])

# -----------------------------
# Profile Layout (placeholder)
# -----------------------------
def profile_layout(session_data):
    username = session_data.get("username") if session_data else "Guest"
    return html.Div([
        dbc.Container([
            html.H2(f"Profile: {username}", style={"marginTop": "30px"}),
            html.P("Profile details would go here.")
        ])
    ])

# -----------------------------
# App Layout
# -----------------------------
app.layout = html.Div([
    dcc.Store(id='user-session', storage_type='session'),

    dbc.NavbarSimple(
        brand="KenSAP",
        color="black",
        dark=True,
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Gallery", href="/gallery")),
            dbc.NavItem(dbc.NavLink("Alumni", href="/alumni")),
            dbc.NavItem(dbc.NavLink("Profile", href="/profile")),
            dbc.NavItem(dbc.NavLink("Logout", href="/logout")),
        ]
    ),

    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),

    html.Footer([
        html.Hr(),
        html.P(
            "© 2025 KenSAP | Designed by Stephen Ntayia",
            style={'textAlign': 'center', 'color': 'white', 'fontSize': '14px', 'marginBottom': '20px'}
        )
    ], style={
        'width': '100%',
        'backgroundColor': 'green',
        'padding': '10px 0',
        'position': 'relative',
        'bottom': '0'
    })
])

# -----------------------------
# Page Routing Callback
# -----------------------------
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('user-session', 'data')
)
def display_page(pathname, session_data):
    if pathname == '/' or pathname == '/login':
        return login_layout
    elif pathname == '/homepage':
        return homepage_layout
    elif pathname == '/gallery':
        return gallery_layout
    elif pathname == '/alumni':
        return alumni_layout
    elif pathname == '/profile':
        return profile_layout(session_data)
    elif pathname == '/logout':
        return html.Div("You have logged out")
    else:
        return login_layout

# -----------------------------
# Authentication Callbacks
# -----------------------------
@app.callback(
    Output("login-output", "children"),
    Output("user-session", "data"),
    Input("login-button", "n_clicks"),
    Input("signup-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def handle_auth(login_click, signup_click, username, password):
    ctx = callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if not username or not password:
        return "Please enter both username and password.", None

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    if button_id == "login-button":
        if username in users and users[username] == password:
            return f"Login successful. Welcome {username}!", {"username": username}
        else:
            return "Invalid username or password.", None

    elif button_id == "signup-button":
        if username in users:
            return "Username already exists. Try logging in.", None
        else:
            users[username] = password
            with open(USERS_FILE, "w") as f:
                json.dump(users, f)
            return f"Sign-up successful! You can now log in, {username}.", None

# -----------------------------
# Logout callback
# -----------------------------
@app.callback(
    Output("user-session", "data"),
    Output("login-output", "children"),
    Input("url", "pathname"),
    State("user-session", "data")
)
def handle_logout(pathname, session_data):
    if pathname == "/logout":
        return None, "You have logged out."
    return session_data, dash.no_update

# -----------------------------
# Alumni callbacks
# -----------------------------
@app.callback(
    Output("alumni-list", "children"),
    Input("alumni-output", "children")
)
def display_alumni(_):
    with open(ALUMNI_FILE, "r") as f:
        alumni = json.load(f)
    if not alumni:
        return html.P("No alumni yet.")
    return html.Ul([html.Li(name) for name in alumni])

@app.callback(
    Output("alumni-output", "children"),
    Input("add-alumni-button", "n_clicks"),
    State("alumni-name-input", "value")
)
def add_alumni(n_clicks, name):
    if not n_clicks:
        return ""
    if not name:
        return "Please enter a valid username."
    with open(ALUMNI_FILE, "r") as f:
        alumni = json.load(f)
    if name in alumni:
        return f"{name} is already in the alumni list."
    alumni.append(name)
    with open(ALUMNI_FILE, "w") as f:
        json.dump(alumni, f)
    return f"{name} has been added to the alumni list!"

# -----------------------------
# Gallery callbacks
# -----------------------------
@app.callback(
    Output({'type': 'comments', 'index': ALL}, 'children'),
    Input({'type': 'submit', 'index': ALL}, 'n_clicks'),
    State({'type': 'input', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def handle_comments(n_clicks_list, comments_list_state):
    ctx = callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    triggered_id = eval(ctx.triggered[0]['prop_id'].split('.')[0])
    photo_name = triggered_id['index']

    input_index = next(i for i, comp in enumerate(ctx.inputs_list[0]) if comp['id']['index'] == photo_name)
    comment_text = comments_list_state[input_index]

    if comment_text and comment_text.strip():
        save_comment(photo_name, comment_text.strip())

    all_comments_children = []
    for filename in os.listdir(PHOTOS_FOLDER):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            comments = get_comments(filename)
            all_comments_children.append(html.Ul([html.Li(c) for c in comments]))
    return all_comments_children

# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host="0.0.0.0", port=port)
