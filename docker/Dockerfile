FROM python:3.10-slim-buster

ENV LANG=C.UTF-8 \
  LC_ALL=C.UTF-8

WORKDIR /app

COPY requirements.txt ./
# HACK: have to patch in some html to add in meta tags/Google Analytics
RUN pip3 install --no-cache-dir -r requirements.txt && \
  cp /usr/local/lib/python3.10/site-packages/streamlit/static/index.html /usr/local/lib/python3.10/site-packages/streamlit/static/index.html.bak && \
  sed -i s'@<title>Streamlit</title>@<!-- Primary Meta Tags --><title>Spire | A viewpoint above Solana data</title><meta name="title" content="Spire | A viewpoint above Solana data"><meta name="description"content="Insights and on-chain data analytics for the Solana blockchain, inspired by the community and accessible to all."><!-- Open Graph / Facebook --><meta property="og:type" content="website"><meta property="og:url" content="https://spire.fyi/"><meta property="og:title" content="Spire | A viewpoint above Solana data"><meta property="og:description"content="Insights and on-chain data analytics for the Solana blockchain, inspired by the community and accessible to all."><meta property="og:image" content="https://github.com/spire-fyi/spire_fyi/raw/main/assets/images/spire_logo_no_background_16_9.png"><!-- Twitter --><meta property="twitter:card" content="summary_large_image"><meta property="twitter:url" content="https://spire.fyi/"><meta property="twitter:title" content="Spire | A viewpoint above Solana data"><meta property="twitter:description"content="Insights and on-chain data analytics for the Solana blockchain, inspired by the community and accessible to all."><meta property="twitter:image" content="https://github.com/spire-fyi/spire_fyi/raw/main/assets/images/spire_logo_no_background_16_9.png">@' /usr/local/lib/python3.10/site-packages/streamlit/static/index.html && \
  sed -i s'@</head>@</head><!-- Google tag (gtag.js) --><script async src="https://www.googletagmanager.com/gtag/js?id=G-MMJV9DVVZ6"></script><script>window.dataLayer = window.dataLayer || [];function gtag(){dataLayer.push(arguments);}gtag('js', new Date());gtag('config', 'G-MMJV9DVVZ6');</script>@' /usr/local/lib/python3.10/site-packages/streamlit/static/index.html
COPY . .
