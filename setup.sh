mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" >> ~/.streamlit/config.toml

echo "\
[flipside]\n\
api_key = \"$FLIPSIDE_API_KEY\"\n\
\n\
" >> ~/.streamlit/secrets.toml
