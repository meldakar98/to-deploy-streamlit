import streamlit as st
import pandas as pd
import json
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

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
def send_email(evaluator_name,subject="Evaluation", to_email="mohamed.ahmedel1133@gmail.com",json_text=None,pdf_path=None,text=None):
    # Deine E-Mail-Adresse und Passwort
    from_email = 'Dok-Pro-KI-Report@web.de'
    password = 'Neur0k@rd#2024#'

    # E-Mail-Server und Port
    smtp_server = 'smtp.web.de'
    port = 587

    # E-Mail-Nachricht erstellen
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject+" by "+evaluator_name

    # Textinhalt der E-Mail
    body = f"Evaluation by {evaluator_name}"
    msg.attach(MIMEText(body, 'plain'))
    if json_text:
        # JSON-Text als .json-Datei anhängen
        json_filename = f"evaluation_data_{evaluator_name}.json"
        with open(json_filename, "w") as f:
            json.dump(json_text, f)
        with open(json_filename, "rb") as f:
            attach = MIMEApplication(f.read(),_subtype="json")
        attach.add_header('Content-Disposition','attachment',filename=str(json_filename))
        msg.attach(attach)

    if pdf_path:
        # PDF-Datei anhängen
        pdf_filename = pdf_path
        with open(pdf_filename, "rb") as f:
            attach = MIMEApplication(f.read(),_subtype="pdf")
        attach.add_header('Content-Disposition','attachment',filename=str(pdf_filename))
        msg.attach(attach)
    if text:
        # Textinhalt der E-Mail
        body = text
        msg.attach(MIMEText(body, 'plain'))

    # Verbindung zum SMTP-Server herstellen und E-Mail senden
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        print("E-Mail gesendet!")
    except Exception as e:
        print(f"Fehler: {e}")
    finally:
        server.quit()
# Update session state initialization
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
            
            display_conversation(current_conversation)

            with st.form(f"survey_form_{current_conversation['id']}"):
                # Add rating questions based on predefined metrics
                effectiveness = st.slider("Effectiveness", 1, 5, 3)
                adaptivity = st.slider("Adaptivity", 1, 5, 3)
                alliance = st.slider("Alliance", 1, 5, 3)
                competence = st.slider("Competence", 1, 5, 3)
                socratic = st.slider("Socratic Dialogue", 1, 5, 3)
                
                # Add text area for comments
                comments = st.text_area("Additional comments", height=100)
                
                # Submit button
                submitted = st.form_submit_button("Submit")
                
                if submitted:
                    # Store results
                    results[current_conversation['id']] = {
                        "effectiveness": effectiveness,
                        "adaptivity": adaptivity,
                        "alliance": alliance,
                        "competence": competence,
                        "socratic": socratic,
                        "comments": comments
                    }
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
            send_email(evaluator_name=st.session_state.username,json_text=st.session_state.selected_conversations)
            
            # Option to download results as a CSV (only shown to administrators)
            if st.sidebar.checkbox("Show Admin Options", False):
                if st.button("Download Results"):
                    df = pd.DataFrame.from_dict(results, orient='index')
                    df.to_csv('evaluation_results.csv')
                    st.success("Results downloaded as evaluation_results.csv")
