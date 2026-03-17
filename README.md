# angol-irasgyakorlo
Egy egyszerű, de hatékony online angol írásgyakorló eszköz, amely valós időben ellenőrzi a szöveget, kiemeli a hibákat, javítási javaslatokat ad, pontosságot (accuracy score) számol, és fel is olvassa a javított szöveget a böngésző beépített TTS (Text-to-Speech) funkciójával.


## Főbb funkciók

- **Valós idejű nyelvtani ellenőrzés és kiejtés** (LanguageTool)
- Két nyelv támogatása: **British English (en-GB)** és **American English (en-US)**
- Hibák **wavy underline** kiemelése tooltip-pel (üzenet + javaslat)
- **Accuracy Score** százalékos értékeléssel (súlyozott hibahossz , súlyos hibák extra büntetés)
- Automatikus javított szöveg generálás + manuális javítások (nagybetű, pont hozzáadása)
- **Hangos felolvasás** a javított szövegről (Web Speech Synthesis API)
- Sötét téma, reszponzív Streamlit felület
- Hibák részletes leírása


## Technológiák

- **Backend**: Python 3.9+
- **Webes felület**: [Streamlit](https://streamlit.io/)
- **Grammar ellenőrzés**: [language-tool-python](https://pypi.org/project/language-tool-python/) (LanguageTool wrapper)
- **Hangos felolvasás**: Web Speech Synthesis API (böngésző beépített TTS)
- **JavaScript integráció**: st.components.v1.html (custom gombok és TTS vezérlés)


