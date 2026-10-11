import os
import streamlit as st
from google import genai
from google.genai import types

# Configuration de la page Streamlit
st.set_page_config(
    page_title="IA IRS - Super-Professeur Universitaire",
    page_icon="🎓",
    layout="wide"
)

# Initialisation du client Google GenAI
st.sidebar.title("🎓 Configuration IA IRS")
api_key = st.sidebar.text_input("Clé API Gemini", type="password", value=os.environ.get("GEMINI_API_KEY", ""))

if not api_key:
    st.warning("⚠️ Veuillez entrer votre clé API Gemini pour démarrer l'assistant.")
    st.stop()

client = genai.Client(api_key=api_key)

# Le Prompt Système : Le Super-Professeur Universitaire Rigoureux
SYSTEM_PROMPT = """
Tu es 'IA IRS', un Super-Professeur d'Université émérite, chercheur intransigeant et pédagogue d'élite. 
Tu aides un étudiant à analyser ses cours (transcriptions audio, notes, résumés) et à progresser avec un niveau d'excellence académique.

Tes compétences clés :
1. **La Double Analyse :** Ne prends jamais les paroles du professeur pour argent comptant. Croise toujours chaque affirmation de cours avec la science établie, les manuels universitaires de référence et la recherche mondiale (via tes capacités de recherche).
2. **La Nuance Pédagogique :** Fais la différence entre une *simplification pédagogique volontaire* (utile pour débuter mais acceptable) et une *erreur factuelle grave* (contresens, fausse formule, date erronée qui pénalisera l'étudiant à l'examen).
3. **Le Rapport de Correction Structuré :** Si une erreur ou un raccourci dangereux est détecté dans le cours, tu dois obligatoirement générer un rapport sous ce format :
   - ⚠️ **ALERTE CORRECTION - [Sujet/Chapitre]**
   - **Ce qu'a dit le professeur :** (Citation ou résumé du propos de l'audio)
   - **Le diagnostic de l'IA :** (Erreur factuelle / Simplification excessive / Obsolescence)
   - **La réalité scientifique / académique :** (Explication rigoureuse et approfondie)
   - **Pourquoi c'est important pour ton examen :** (Impact sur la note/compréhension)
4. **Pédagogie socratique :** Après tes explications et corrections, pose toujours une question de réflexion à l'étudiant pour t'assurer qu'il a bien saisi la nuance.
"""

# Interface principale
st.title("🎓 IA IRS : Ton Super-Professeur Universitaire")
st.markdown("Importe la transcription de ton cours ou pose une question. IA IRS réalisera une double analyse critique et te protégera contre les erreurs de cours !")

# Zone de saisie du cours ou de la question
cours_input = st.text_area(
    "📝 Colle ici le contenu de ton cours (ou la transcription audio de ton professeur) :",
    height=200,
    placeholder="Ex: Aujourd'hui en cours de biologie, le professeur a dit que..."
)

question_input = st.text_input(
    "❓ As-tu une question spécifique sur ce cours ou une demande de révision particulière ?",
    placeholder="Ex: Peux-tu vérifier ce passage et me faire un quiz ?"
)

if st.button("Lancer l'Analyse Académique 🚀", type="primary"):
    if not cours_input and not question_input:
        st.error("Veuillez fournir au moins un texte de cours ou une question.")
    else:
        with st.spinner("🎓 IA IRS analyse, croise les sources et prépare son rapport académique..."):
            try:
                user_content = f"""
                Voici le contenu du cours fourni par l'étudiant :
                ---
                {cours_input if cours_input else "Aucun texte de cours spécifique fourni pour l'instant."}
                ---
                
                Question / Requête de l'étudiant :
                {question_input if question_input else "Fais une analyse critique complète de ce cours, détecte les erreurs potentielles et explique les notions."}
                """

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_content,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.3,
                        tools=[{"google_search": {}}],
                    ),
                )

                st.success("Analyse terminée !")
                st.markdown("### 🎓 Rapport et Explications d'IA IRS")
                st.markdown(response.text)

                if response.candidates and response.candidates[0].grounding_metadata:
                    metadata = response.candidates[0].grounding_metadata
                    if hasattr(metadata, 'web_search_queries') and metadata.web_search_queries:
                        with st.expander("🔍 Sources et recherches web utilisées par IA IRS"):
                            st.write("Requêtes de vérification :", metadata.web_search_queries)

            except Exception as e:
                st.error(f"Une erreur est survenue lors de l'appel à l'API : {e}")

# Section d'aide dans la sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Astuce d'utilisation")
st.sidebar.markdown(
    "1. Enregistre ton cours avec ton téléphone.\n"
    "2. Transcris-le en texte (via Whisper ou dictaphone).\n"
    "3. Colle le texte ici pour que **IA IRS** traque les erreurs de ton professeur et t'offre un cours magistral irréprochable !"
)
