import io
import os
from google import genai
from gtts import gTTS
import streamlit as st
from weasyprint import HTML

# Configuration de la page Streamlit
st.set_page_config(
    page_title="IA IRS - Super-Professeur", page_icon="🎓", layout="centered"
)

# Style CSS épuré et moderne
st.markdown(
    """
    <style>
    .main { background-color: #faf8f5; }
    h1 { color: #1e293b; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { background-color: #ef4444; color: white; border-radius: 8px; font-weight: bold; width: 100%; border: none; padding: 10px; }
    .stButton>button:hover { background-color: #dc2626; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎓 IA IRS — Super-Professeur & Fact-Checker")
st.markdown(
    "*Votre assistant académique rigoureux : analyse critique, fact-checking,"
    " exercices, résumés et mémorisation rapide.*"
)

# Barre latérale pour la configuration
with st.sidebar:
  st.header("⚙️ Configuration IA IRS")
  api_key_input = st.text_input(
      "Clé API Gemini", type="password", help="Entrez votre clé API Google GenAI"
  )

  api_key = api_key_input
  if not api_key:
    try:
      api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
      pass

  st.divider()
  st.markdown("### 💡 Guide d'utilisation")
  st.markdown(
      "1. Saisissez votre clé API Gemini.\n2. Importez ou collez votre support"
      " (Texte, Audio, Image, PDF).\n3. L'IA génère une analyse rigoureuse,"
      " des exemples, des exercices, un résumé et des astuces mnémotechniques.\n4."
      " Écoutez ou téléchargez le tout en PDF !"
  )

if not api_key:
  st.warning(
      "⚠️ Veuillez entrer votre clé API Gemini dans le volet latéral pour"
      " démarrer l'assistant."
  )
  st.stop()

try:
  client = genai.Client(api_key=api_key)
except Exception as e:
  st.error(f"Erreur d'initialisation du client Gemini : {e}")
  st.stop()

# --- SECTION ENTRÉE MULTIMÉDIA ---
st.markdown("### 📂 Importation de votre cours ou support")

input_mode = st.radio(
    "Choisissez le format d'entrée :",
    [
        "Texte ou Transcription directe",
        "Fichier Audio / Document / Image",
        "Enregistrement Dictaphone (Micro)",
    ],
    horizontal=True,
)

course_content = ""
uploaded_file = None

if input_mode == "Texte ou Transcription directe":
  course_content = st.text_area(
      "Collez ici le contenu brut de votre cours ou notes de transcription :",
      height=150,
      placeholder=(
          "Ex: Aujourd'hui en cours de biologie, le professeur a expliqué..."
      ),
  )

elif input_mode == "Fichier Audio / Document / Image":
  uploaded_file = st.file_uploader(
      "Importez un fichier (Audio MP3/WAV, Image PNG/JPG, Document PDF ou Texte):",
      type=["mp3", "wav", "m4a", "png", "jpg", "jpeg", "pdf", "txt"],
  )
  if uploaded_file is not None:
    st.success(f"Fichier chargé avec succès : {uploaded_file.name}")
    if uploaded_file.type.startswith("text"):
      course_content = uploaded_file.getvalue().decode("utf-8")
    elif uploaded_file.type.startswith("image") or uploaded_file.type == (
        "application/pdf"
    ):
      st.info(
          "📸 Fichier multimédia pris en compte. Il sera analysé directement"
          " par l'intelligence artificielle."
      )

elif input_mode == "Enregistrement Dictaphone (Micro)":
  audio_bytes = st.audio_input(
      "Enregistrez votre cours ou dictée directement via le micro de votre"
      " téléphone :"
  )
  if audio_bytes is not None:
    st.audio(audio_bytes, format="audio/wav")
    uploaded_file = audio_bytes
    st.success("🎙️ Audio enregistré avec succès !")

user_question = st.text_input(
    "❓ Avez-vous une question spécifique ou une consigne particulière ?",
    placeholder="Ex: Insiste bien sur les formules de physique.",
)

# --- BOUTON D'ANALYSE ---
if st.button("Lancer l'Analyse Académique & Pédagogique 🚀"):
  if not course_content and not uploaded_file:
    st.error(
        "Veuillez fournir du texte, un fichier ou un enregistrement audio avant"
        " de lancer l'analyse."
    )
  else:
    with st.spinner(
        "🔄 Analyse critique, création d'exercices et de méthodes mnémotechniques"
        " en cours..."
    ):
      try:
        # Prompt enrichi pour inclure exemples, exercices, réponses, résumé et mémorisation rapide
        prompt_system = (
            "Tu es 'IA IRS', un Super-Professeur académique, extrêmement"
            " rigoureux, critique et socratique. Ton rôle est d'analyser les"
            " cours ou notes d'étudiants, de détecter les erreurs"
            " scientifiques/factuelles, et de structurer un rapport complet"
            " contenant obligatoirement les sections suivantes :\n"
            "1. 🔍 **Analyse critique & Fact-checking** (vérification des erreurs"
            " du professeur ou du cours).\n"
            "2. 💡 **Exemples concrets** pour illustrer les notions clés.\n"
            "3. 📝 **Exercices d'application** adaptés au niveau.\n"
            "4. ✅ **Réponses / Corrigés détaillés** des exercices.\n"
            "5. 📌 **Résumé magistral** de la leçon.\n"
            "6. 🧠 **Méthode à mémorisation rapide (À retenir)** :"
            " moyens mnémotechniques, astuces ou phrases clés pour retenir"
            " l'essentiel instantanément."
        )

        contents_payload = []
        contents_payload.append(prompt_system)

        if course_content:
          contents_payload.append(f"Contenu du cours fourni : {course_content}")

        if uploaded_file is not None:
          bytes_data = uploaded_file.getvalue()
          mime_type = getattr(uploaded_file, "type", "audio/wav")
          contents_payload.append(
              genai.types.Part.from_bytes(data=bytes_data, mime_type=mime_type)
          )

        if user_question:
          contents_payload.append(f"Consigne / Question : {user_question}")
        else:
          contents_payload.append(
              "Traite l'ensemble des sections requises de manière claire et"
              " structurée."
          )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents_payload,
            config=genai.types.GenerateContentConfig(
                tools=[{"google_search": {}}], temperature=0.2
            ),
        )

        analysis_result = response.text
        st.session_state["last_analysis"] = analysis_result
        st.success(
            "✨ Analyse et supports pédagogiques générés avec succès !"
        )

      except Exception as e:
        st.error(f"Erreur lors de l'analyse avec l'API Gemini : {e}")

# --- AFFICHAGE DES RÉSULTATS & OPTIONS AVANCÉES ---
if "last_analysis" in st.session_state:
  st.divider()
  st.subheader("📋 Rapport Pédagogique Complet - IA IRS")
  st.markdown(st.session_state["last_analysis"])

  col1, col2 = st.columns(2)

  # 1. Option de Synthèse Vocale
  with col1:
    if st.button("🔊 Écouter la réponse audio"):
      with st.spinner("Génération de la synthèse vocale..."):
        try:
          tts = gTTS(text=st.session_state["last_analysis"], lang="fr")
          audio_io = io.BytesIO()
          tts.write_to_fp(audio_io)
          audio_io.seek(0)
          st.audio(audio_io, format="audio/mp3")
        except Exception as e:
          st.error(f"Erreur lors de la génération audio : {e}")

  # 2. Option de Téléchargement PDF
  with col2:
    if st.button("📥 Télécharger le rapport en PDF"):
      with st.spinner("Génération du document PDF..."):
        try:
          html_content = f"""
                    <!DOCTYPE html>
                    <html lang="fr">
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            @page {{ size: A4; margin: 20mm; background-color: #ffffff; }}
                            body {{ font-family: Arial, sans-serif; color: #1e293b; line-height: 1.6; font-size: 11pt; }}
                            h1 {{ color: #dc2626; border-bottom: 2px solid #dc2626; padding-bottom: 5px; }}
                            h2, h3 {{ color: #1e293b; margin-top: 20px; }}
                            p, li {{ margin-bottom: 8px; }}
                            .footer {{ margin-top: 30px; font-size: 9pt; color: #64748b; text-align: center; border-top: 1px solid #cbd5e1; padding-top: 10px; }}
                        </style>
                    </head>
                    <body>
                        <h1>Rapport Pédagogique - IA IRS</h1>
                        <p><em>Correction, Exemples, Exercices & Mémorisation Rapide</em></p>
                        <hr>
                        <div>
                            {st.session_state["last_analysis"].replace(chr(10), '<br>')}
                        </div>
                        <div class="footer">
                            Généré par IA IRS - Super-Professeur | Conforme aux sources académiques vérifiées.
                        </div>
                    </body>
                    </html>
                    """
          pdf_path = "/tmp/Rapport_IA_IRS.pdf"
          HTML(string=html_content).write_pdf(pdf_path)

          with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="💾 Cliquer ici pour télécharger le PDF",
                data=pdf_file,
                file_name="Rapport_IA_IRS.pdf",
                mime="application/pdf",
            )
        except Exception as e:
          st.error(f"Erreur lors de la création du PDF : {e}")
