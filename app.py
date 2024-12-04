import streamlit as st
import pandas as pd
import json
import utils
from datetime import datetime  # Add this import

def load_credentials():
    try:
        # Get credentials from streamlit secrets
        return st.secrets["credentials"]
    except Exception as e:
        st.error("Error loading credentials")
        return {"experts": []}
def verify_credentials(username, password, credentials):
    for expert in credentials["experts"]:
        if expert["username"] == username and expert["password"] == password:
            # Return tuple of (is_authenticated, is_admin)
            return True, expert.get("is_admin", False)
    return False, False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# Add these session state initializations
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if "start_evaluation" not in st.session_state:
    st.session_state.start_evaluation = False
# Load conversations from JSON files
def load_conversations(file_path):
    with open(file_path,encoding='utf-8') as f:
        return json.load(f)

# Save updated conversations back to JSON file
def save_conversations(file_path, new_conversations):
    try:
        with open(file_path, 'r') as f:
            existing_conversations = json.load(f)
    except FileNotFoundError:
        existing_conversations = []
    
    existing_conversations.extend(new_conversations)
    
    with open(file_path, 'w') as f:
        json.dump(existing_conversations, f, ensure_ascii=False, indent=4)

# Paths to the JSON files

# Initialize session state for current conversation index and selected conversations

# Add login page before the main survey
if not st.session_state.logged_in:
    st.title("Expert Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            credentials = load_credentials()
            is_authenticated, is_admin = verify_credentials(username, password, credentials)
            if is_authenticated:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.is_admin = is_admin
                utils.send_email(evaluator_name=st.session_state.username+datetime.now().strftime("%m-%d:%H"),text="erfolgreich eingeloggt")
                st.rerun()
            else:
                st.error("Invalid credentials")
else:
    if st.session_state.is_admin:
        st.sidebar.markdown("### Admin Controls")
        if st.sidebar.button("Download All Results"):
            # Load both rated files
            try:
                
                
                # Create download button
                st.sidebar.download_button(
                    label="Download JSON",
                    data=json.dumps(st.session_state.results, ensure_ascii=False, indent=4).encode('utf-8'),
                    file_name='all_evaluations.json',
                    mime='application/json'
                )
            except FileNotFoundError:
                st.sidebar.error("No evaluation results found yet")
    else:
        if st.session_state.start_evaluation:
            if 'current_index' not in st.session_state:
                st.session_state.current_index = 0
            if 'results' not in st.session_state:
                st.session_state.results = []
                
            if 'selected_conversations' not in st.session_state:
                # Load conversations
                #TODO: Modify loading from username
                conversations1 = load_conversations("./data/data.json")
                st.session_state.selected_conversations = conversations1[st.session_state.username]

            # Create a dictionary to store results
            results = {}

            # Function to display the current conversation
            def display_conversation(conversation):
                st.subheader(f"Conversation ID: {conversation['id']}")
                
                # Display the conversation
                st.write("### Conversation:")
                for turn in conversation['conversation']:
                    st.write(f"**{turn['role'].capitalize()}:** {turn['content']}")

            # Main application logic
            st.title("Expert Evaluation Survey")

            # Add custom CSS to change the slider color to blue
            st.markdown(
                """
                <style>
                .stSlider .st-bj {
                    background-color: blue; /* Background of the slider */
                }
                .stSlider .st-bj .st-bk {
                    background-color: blue; /* Background of the slider track */
                }
                .stSlider .st-bj .st-bk .st-bk {
                    background-color: blue; /* Background of the slider track */
                }
                .stSlider .st-bj .st-bk .st-bk .st-bk {
                    background-color: blue; /* Background of the slider track */
                }
                </style>
                """,
                unsafe_allow_html=True
            )


            # Check if there are more conversations to evaluate
            if st.session_state.current_index < len(st.session_state.selected_conversations):
                current_conversation = st.session_state.selected_conversations[st.session_state.current_index]
                
                # Display the conversation in the main area
                display_conversation(current_conversation)

                # Display the evaluation form in the sidebar
                with st.sidebar:
                    st.markdown("### Evaluation Form ",help="- ⭐️ sehr schlecht \n - ⭐️⭐️ schlecht \n - ⭐️⭐️⭐️ befriedigend \n - ⭐️⭐️⭐️⭐️ gut \n - ⭐️⭐️⭐️⭐️⭐️ ausgezeichnet")
                    with st.form(f"survey_form_{current_conversation['id']}"):
                        # Add rating questions based on predefined metrics
                        effectiveness = st.slider("Wirksamkeit bei der Reduktion kognitiver Verzerrungen", 1, 5, 3,help="Wirksamkeit bei der Reduktion kognitiver Verzerrungen \n - Erkennung der Verzerrungen \n - Erfolgreiche Intervention \n - Messbare Veränderung im Gesprächsverlauf ")
                        adaptivity = st.slider("Adaptivität und Individualisierung", 1, 5, 3,help="Adaptivität und Individualisierung \n - Anpassung an individuelle Bedürfnisse \n - Flexibilität bei verschiedenen Verzerrungsarten \n - Berücksichtigung persönlicher Umstände ")
                        alliance = st.slider("Therapeutische Allianz", 1, 5, 3,help="Therapeuten Beziehung  \n - Empathie und Verständnis \n - Vertrauensaufbau \n - Gemeinsame Entscheidungsfindung \n ")
                        competence = st.slider("Therapeutische Kompetenz", 1, 5, 3,help="Therapeutische Kompetenz \n - Präzise Identifikation von Verzerrungen \n - Effektive Interventionsauswahl \n - Professionelle Gesprächsführung \n ")
                        socratic = st.slider("Sokratischer Dialog", 1, 5, 3,help="Sokratischer Dialog \n - Geschickte Frageführung \n - Förderung der Selbstreflexion \n - Unterstützung bei eigener Erkenntnisfindung \n")
                        
                        # Add text area for comments
                        comments = st.text_area("Begründung für die Bewertung", height=100)
                        
                        # Submit button
                        submitted = st.form_submit_button("Submit")
                        
                        if submitted:
                            # Store results
                            results[current_conversation['id']] = {
                                "Wirksamkeit bei der Reduktion kognitiver Verzerrungen": effectiveness,
                                "Adaptivität und Individualisierung": adaptivity,
                                "Therapeutische Allianz": alliance,
                                "Therapeutische Kompetenz": competence,
                                "Sokratischer Dialog": socratic,
                                "begründung": comments
                            }
                            st.session_state.results.append(utils.fit_into_dialoug_schema(current_conversation['id'],current_conversation['conversation'],current_conversation['label'],current_conversation['evaluations'],results[current_conversation['id']],f"expert_{st.session_state.username}"))
                            st.success("Thank you for your feedback!")

                            # Update the conversation with the evaluation
                            current_conversation['evaluations'].append(results[current_conversation['id']])

                            # Move to the next conversation
                            st.session_state.current_index += 1
                            st.rerun()

                            
            else:
                # Thank you screen
                st.markdown(
                    """
                    <div style="text-align: center; padding: 50px;">
                        <h1>Vielen Dank!</h1>
                        <p style="font-size: 20px;">Wir danken Ihnen für Ihre Zeit und Mühe bei der Bewertung dieser Gespräche.</p>
                        <p style="font-size: 18px;">Ihre Expertinnen-Rückmeldungen sind uns wertvoll für unsere Forschung.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.write("### Bitte geben Sie ihren Namen ein")
                name = st.text_input("Name")
                if st.button("Send Results"):
                    utils.send_email(evaluator_name=name+ " from " +st.session_state.username+" "+datetime.now().strftime("%m-%d:%H"),json_text=st.session_state.results)
                    st.session_state.clear()
                    st.rerun()

                # Option to download results as a CSV (only shown to administrators)
                if st.sidebar.checkbox("Show Admin Options", False):
                    if st.button("Download Results"):
                        df = pd.DataFrame.from_dict(results, orient='index')
                        df.to_csv('evaluation_results.csv')
                        st.success("Results downloaded as evaluation_results.csv")
                    if st.button("Restart App"):
                        st.session_state.clear()
                        st.experimental_rerun()
        else:
            st.title("Start Evaluation")
            st.markdown("""# Vielen Dank für Ihre Unterstützung!

Vielen Dank, dass Sie sich die Zeit genommen haben, uns bei der Evaluation der Gespräche zu unterstützen. Diese Studie zielt darauf ab, die Fähigkeit von KI-Assistenten zu analysieren und zu bewerten, wie gut solche Systeme helfen können, kognitive Verzerrungen zu reduzieren.

In dieser Studie werden Ihnen generierte Gespräche zwischen einem KI-Patienten und einem KI-Assistenten präsentiert. Die Hälfte der Gespräche stammt von einem **GPT-4o-Modell**, die andere Hälfte wurde von einem **optimierten FT:GPT-3.5-Turbo-1106-Modell** generiert. Ziel ist es, die Fähigkeit der KI-Assistenten zu bewerten, kognitive Verzerrungen zu erkennen und zu reduzieren, sowie die Effektivität unserer Optimierungen zu analysieren.

## Ziel der Studie
Die Hauptziele dieser Studie sind:
- Die Analyse der Erkennung und Reduktion kognitiver Verzerrungen durch KI-Assistenten.
- Die Bewertung, ob Optimierungen der KI-Assistenten die Leistung und Qualität der Gespräche verbessern.

## Evaluationsmetriken
Die Gespräche sollen anhand der folgenden Kriterien bewertet werden:

### 1. **Wirksamkeit bei der Reduktion kognitiver Verzerrungen**
- **Erkennung der Verzerrungen**
- **Erfolgreiche Intervention**
- **Messbare Veränderung im Gesprächsverlauf**

**Bewertungsskala:**
- ⭐️ 1 Stern: Sehr schlecht – Kognitive Verzerrungen werden nicht erkannt oder vollständig ignoriert.
- ⭐️⭐️ 2 Sterne: Schlecht – Einige Verzerrungen werden erkannt, jedoch unvollständig oder fehlerhaft.
- ⭐️⭐️⭐️ 3 Sterne: Befriedigend – Die meisten Verzerrungen werden erkannt, aber es gibt Verbesserungspotenzial.
- ⭐️⭐️⭐️⭐️ 4 Sterne: Gut – Verzerrungen werden klar und größtenteils genau identifiziert.
- ⭐️⭐️⭐️⭐️⭐️ 5 Sterne: Ausgezeichnet – Alle Verzerrungen werden präzise und umfassend erkannt.

---

### 2. **Adaptivität und Individualisierung**
- **Anpassung an individuelle Bedürfnisse**
- **Flexibilität bei verschiedenen Verzerrungsarten**
- **Berücksichtigung persönlicher Umstände**

**Bewertungsskala:**
- ⭐️ 1 Stern: Sehr schlecht – Keine Anpassung an individuelle Umstände oder Bedürfnisse.
- ⭐️⭐️ 2 Sterne: Schlecht – Eingeschränkte Anpassung; viele Bedürfnisse bleiben unberücksichtigt.
- ⭐️⭐️⭐️ 3 Sterne: Befriedigend – Angemessene Anpassung mit einigen Lücken.
- ⭐️⭐️⭐️⭐️ 4 Sterne: Gut – Gute Flexibilität und Individualisierung mit geringfügigen Verbesserungsmöglichkeiten.
- ⭐️⭐️⭐️⭐️⭐️ 5 Sterne: Ausgezeichnet – Hervorragende Anpassung an individuelle Umstände und Bedürfnisse.

---

### 3. **Therapeuten-Beziehung**
- **Empathie und Verständnis**
- **Vertrauensaufbau**
- **Gemeinsame Entscheidungsfindung**

**Bewertungsskala:**
- ⭐️ 1 Stern: Sehr schlecht – Keine Empathie oder Vertrauensaufbau.
- ⭐️⭐️ 2 Sterne: Schlecht – Begrenzte Empathie und ein schwaches Vertrauen.
- ⭐️⭐️⭐️ 3 Sterne: Befriedigend – Angemessenes Verständnis und Vertrauen, aber mit Verbesserungspotenzial.
- ⭐️⭐️⭐️⭐️ 4 Sterne: Gut – Gute Empathie und kooperativer Ansatz.
- ⭐️⭐️⭐️⭐️⭐️ 5 Sterne: Ausgezeichnet – Höchstmaß an Empathie, Vertrauen und Zusammenarbeit.

---

### 4. **Therapeutische Kompetenz**
- **Präzise Identifikation von Verzerrungen**
- **Effektive Interventionsauswahl**
- **Professionelle Gesprächsführung**

**Bewertungsskala:**
- ⭐️ 1 Stern: Sehr schlecht – Verzerrungen werden nicht erkannt, und Interventionen sind ineffektiv.
- ⭐️⭐️ 2 Sterne: Schlecht – Unzureichende Präzision bei der Identifikation oder Auswahl der Intervention.
- ⭐️⭐️⭐️ 3 Sterne: Befriedigend – Akzeptable Kompetenz mit deutlichem Verbesserungspotenzial.
- ⭐️⭐️⭐️⭐️ 4 Sterne: Gut – Kompetente Identifikation und Interventionen mit minimalen Schwächen.
- ⭐️⭐️⭐️⭐️⭐️ 5 Sterne: Ausgezeichnet – Höchste Professionalität in Identifikation und Interventionen.

---

### 5. **Sokratischer Dialog**
- **Geschickte Frageführung**
- **Förderung der Selbstreflexion**
- **Unterstützung bei eigener Erkenntnisfindung**

**Bewertungsskala:**
- ⭐️ 1 Stern: Sehr schlecht – Keine Förderung von Reflexion oder Erkenntnis.
- ⭐️⭐️ 2 Sterne: Schlecht – Begrenzte Frageführung und Förderung der Reflexion.
- ⭐️⭐️⭐️ 3 Sterne: Befriedigend – Ausreichende Unterstützung, aber mit Schwächen.
- ⭐️⭐️⭐️⭐️ 4 Sterne: Gut – Gute Frageführung und Selbstreflexionsförderung.
- ⭐️⭐️⭐️⭐️⭐️ 5 Sterne: Ausgezeichnet – Herausragende Unterstützung bei Erkenntnisfindung und Reflexion.

---

## Ablauf der Evaluation
1. **Beispielgespräch:** Zunächst wird ein Beispiel gezeigt, das Sie bewerten können. Diese Bewertung wird jedoch nicht gespeichert.
2. **Gesprächsbewertung:** Bewerten Sie die bereitgestellten Gespräche anhand der oben genannten Kriterien.
3. **Abschluss:** Am Ende können Sie Ihren Namen eingeben, wenn Sie möchten, dass er in der Studie erwähnt wird.

Sie können das Bewertungsformular auch mehrmals ausfüllen.

---

## Nochmals vielen Dank!
Ihre Hilfe ist für den Erfolg dieser Studie von unschätzbarem Wert.
""")
            if st.button("Start Evaluation"):
                st.session_state.start_evaluation = True
                st.rerun()
