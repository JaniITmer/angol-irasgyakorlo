import streamlit as st
import language_tool_python

@st.cache_resource
def get_tool(dialect_code='en-GB'):
    return language_tool_python.LanguageToolPublicAPI(dialect_code)

def calculate_accuracy(text: str, matches) -> int:
    if not text.strip():
        return 100
    
    total_chars = len(text)
    error_chars = sum(m.error_length for m in matches)
    
    error_ratio = error_chars / total_chars if total_chars > 0 else 0
    score = 100 - (error_ratio * 150)
    
    serious_count = sum(1 for m in matches if m.category in ["CASING", "PUNCTUATION", "TYPOGRAPHY"])
    score -= serious_count * 10
    
    return max(0, min(100, round(score)))

st.set_page_config(page_title="Angol Írásgyakorló", layout="wide")
st.title("Angol írásgyakorló – Grammar Checker")

dialect = st.selectbox(
    "Válassz dialektust",
    ["British English (en-GB)", "American English (en-US)"],
    index=0
)
dialect_code = "en-GB" if "British" in dialect else "en-US"

text = st.text_area(
    "Írj egy mondatot vagy bekezdést...",
    height=140,
    placeholder="Példa: yesterday I was thinking about learning new things"
)

if st.button("Ellenőrizd / Analyze"):
    if text.strip():
        with st.spinner("Ellenőrzés folyamatban..."):
            tool = get_tool(dialect_code)
            matches = tool.check(text)
            
            score = calculate_accuracy(text, matches)
            st.subheader(f"Accuracy Score: {score}%")
            
            if not matches:
                st.success("Tökéletes! Nincs javítanivaló. 🎉")
                st.balloons()
            else:
                
                highlighted = text
                offset_delta = 0
                
                for match in sorted(matches, key=lambda m: m.offset):
                    start = match.offset + offset_delta
                    end = start + match.error_length
                    
                    bad_part = highlighted[start:end]
                    suggestion = match.replacements[0] if match.replacements else bad_part
                    
                    tooltip = f"{match.message}\nJavaslat: {suggestion}"
                    tooltip = tooltip.replace('"', '&quot;').replace("'", "&#39;").replace("\n", "&#10;")
                    
                    span_html = (
                        f'<span style="text-decoration: wavy underline #ea4335; '
                        f'cursor: help; position: relative;" '
                        f'title="{tooltip}">{bad_part}</span>'
                    )
                    
                    highlighted = highlighted[:start] + span_html + highlighted[end:]
                    offset_delta += len(span_html) - len(bad_part)
                
                st.markdown(
                    f'<div style="background:#1e1e2e; padding:16px; border-radius:8px; '
                    f'border:1px solid #444; white-space:pre-wrap; word-wrap:break-word;">'
                    f'{highlighted}</div>',
                    unsafe_allow_html=True
                )
            
            
            corrected = language_tool_python.utils.correct(text, matches)
            
            if corrected and not corrected[0].isupper():
                corrected = corrected[0].upper() + corrected[1:]
            
            if corrected and not corrected.strip().endswith(('.', '!', '?')):
                corrected += "."
            
            st.info(f"**Javasolt javított verzió:**  \n{corrected}")
            
           
            if matches:
                with st.expander("Részletes hibák"):
                    for m in matches:
                        st.write(f"**{m.category}** – {m.message}")
                        if m.replacements:
                            st.caption(f"Javaslatok: {', '.join(m.replacements[:3])}")
                        st.markdown("---")
            
            speak_text = corrected if corrected and corrected.strip() else text
            dialect_lang = "en-GB" if dialect_code == "en-GB" else "en-US"
            escaped_text = speak_text.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
            
            html_component = f"""
            <div style="margin-top: 24px; padding: 12px; background: #2d2d44; border-radius: 8px; border: 1px solid #555;">
                <button id="speakBtn" style="padding:12px 24px; background:#4CAF50; color:white; border:none; border-radius:6px; cursor:pointer; font-size:16px; min-width:180px;">
                    🔊 Felolvasás
                </button>
            </div>

            <script>
            const speakBtn = document.getElementById('speakBtn');
            let speaking = false;
            let voicesLoaded = false;

           
            speechSynthesis.onvoiceschanged = function() {{
                voicesLoaded = true;
                console.log('Hangok betöltve:', speechSynthesis.getVoices().length + ' db');
            }};

            speakBtn.addEventListener('click', function() {{
                if (speaking) {{
                    speechSynthesis.cancel();
                    speakBtn.innerHTML = '🔊 Felolvasás';
                    speakBtn.style.background = '#4CAF50';
                    speaking = false;
                    return;
                }}

                if ('speechSynthesis' in window) {{
                    // Ha a hangok még nem töltődtek be, várunk 1-2 másodpercet
                    if (!voicesLoaded) {{
                        speakBtn.innerHTML = 'Töltődik...';
                        setTimeout(() => {{
                            if (voicesLoaded) startSpeaking();
                            else alert('Hangok nem töltődtek be. Próbáld újra később.');
                        }}, 1800);
                        return;
                    }}
                    startSpeaking();
                }} else {{
                    alert('A böngésző nem támogatja a hangos felolvasást.');
                }}

                function startSpeaking() {{
                    const ut = new SpeechSynthesisUtterance(`{escaped_text}`);
                    ut.lang = '{dialect_lang}';
                    ut.rate = 1.0;
                    ut.pitch = 1.0;
                    ut.volume = 1.0;

                    const voices = speechSynthesis.getVoices();
                    let voice = voices.find(v => v.lang === '{dialect_lang}');
                    if (!voice) voice = voices.find(v => v.lang.startsWith('{dialect_lang.split("-")[0]}'));
                    if (voice) ut.voice = voice;

                    speechSynthesis.speak(ut);

                    speakBtn.innerHTML = '⏹️ Leállítás';
                    speakBtn.style.background = '#f44336';
                    speaking = true;

                    ut.onend = function() {{
                        speakBtn.innerHTML = '🔊 Felolvasás';
                        speakBtn.style.background = '#4CAF50';
                        speaking = false;
                    }};

                    ut.onerror = function(e) {{
                        console.error('Felolvasási hiba:', e.error);
                        alert('Hiba történt a felolvasás közben: ' + (e.error || 'ismeretlen'));
                    }};
                }}
            }});
            </script>
            """

            st.components.v1.html(html_component, height=120)
    else:
        st.warning("Írj be legalább egy mondatot előbb!")

st.caption("Powered by LanguageTool • Java 17+ szükséges")