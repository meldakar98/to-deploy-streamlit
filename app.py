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
file1_path = './data/unrated/gpt-4o-generated-finished.json'
file2_path = './data/unrated/ft:gpt-3.5-turbo-1106:personal::8p2K32Em-generated-finished.json'

# Initialize session state for current conversation index and selected conversations
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

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
                st.rerun()
            else:
                st.error("Invalid credentials")
else:
    if st.session_state.is_admin:
        st.sidebar.markdown("### Admin Controls")
        if st.sidebar.button("Download All Results"):
            # Load both rated files
            try:
                with open(file1_path+"rated.json") as f:
                    rated1 = json.load(f)
                with open(file2_path+"rated.json") as f:
                    rated2 = json.load(f)
                
                # Combine all evaluations
                all_evaluations = rated1 + rated2
                
                # Create download button
                st.sidebar.download_button(
                    label="Download JSON",
                    data=json.dumps(all_evaluations, ensure_ascii=False, indent=4).encode('utf-8'),
                    file_name='all_evaluations.json',
                    mime='application/json'
                )
            except FileNotFoundError:
                st.sidebar.error("No evaluation results found yet")
    else:
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
                st.markdown("### Evaluation Form")
                with st.form(f"survey_form_{current_conversation['id']}"):
                    # Add rating questions based on predefined metrics
                    effectiveness = st.slider("Wirksamkeit bei der Reduktion kognitiver Verzerrungen", 1, 5, 3)
                    st.write("Wirksamkeit bei der Reduktion kognitiver Verzerrungen - Erkennung der Verzerrungen - Erfolgreiche Intervention - Messbare Veränderung im Gesprächsverlauf ")
                    adaptivity = st.slider("Adaptivität und Individualisierung", 1, 5, 3)
                    st.write("Adaptivität und Individualisierung - Anpassung an individuelle Bedürfnisse - Flexibilität bei verschiedenen Verzerrungsarten - Berücksichtigung persönlicher Umstände")
                    alliance = st.slider("Therapeutische Allianz", 1, 5, 3)
                    st.write("Therapeutische Allianz - Empathie und Verständnis - Vertrauensaufbau - Gemeinsame Entscheidungsfindung")
                    competence = st.slider("Therapeutische Kompetenz", 1, 5, 3)
                    st.write("Therapeutische Kompetenz - Präzise Identifikation von Verzerrungen - Effektive Interventionsauswahl - Professionelle Gesprächsführung")
                    socratic = st.slider("Sokratischer Dialog", 1, 5, 3)
                    st.write("Sokratischer Dialog - Geschickte Frageführung - Förderung der Selbstreflexion - Unterstützung bei eigener Erkenntnisfindung")
                    
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
                    <h1>Thank You!</h1>
                    <p style="font-size: 20px;">We appreciate your time and effort in evaluating these conversations.</p>
                    <p style="font-size: 18px;">Your expert feedback is invaluable to our research.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            utils.send_email(evaluator_name=st.session_state.username+datetime.now().strftime("%m-%d:%H"),json_text=st.session_state.results)
            
            # Option to download results as a CSV (only shown to administrators)
            if st.sidebar.checkbox("Show Admin Options", False):
                if st.button("Download Results"):
                    df = pd.DataFrame.from_dict(results, orient='index')
                    df.to_csv('evaluation_results.csv')
                    st.success("Results downloaded as evaluation_results.csv")
