import streamlit as st
import pandas as pd
import json
import random
import os


def load_credentials(file_path):
    try:
        with open(file_path) as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Credentials file not found")
        return {"experts": []}
def verify_credentials(username, password, credentials):
    for expert in credentials["experts"]:
        if expert["username"] == username and expert["password"] == password:
            # Return tuple of (is_authenticated, is_admin)
            return True, expert.get("is_admin", False)
    return False, False

# Update session state initialization
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# Add these session state initializations
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
# Load conversations from JSON files
def load_conversations(file_path):
    with open(file_path) as f:
        return json.load(f)
print("loaded")
# Save updated conversations back to JSON file
def save_conversations(file_path, conversations):
    with open(file_path, 'w') as f:
        print(conversations)
        json.dump(conversations, f, ensure_ascii=False, indent=4)

# Paths to the JSON files
file1_path = '/Users/meldakar/Desktop/Uni/Bachelor/BA/Code/Evaluation/data/generated/gpt-4o-generated-finished.json'
file2_path = '/Users/meldakar/Desktop/Uni/Bachelor/BA/Code/Evaluation/data/generated/ft:gpt-3.5-turbo-1106:personal::8p2K32Em-generated-finished.json'

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
            credentials = load_credentials('/Users/meldakar/Desktop/Uni/Bachelor/BA/Code/Evaluation/data/credentials.json')
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
            conversations1 = load_conversations(file1_path)
            conversations2 = load_conversations(file2_path)

            # Store original conversations in session state
            st.session_state.conversations1 = conversations1
            st.session_state.conversations2 = conversations2

            # Combine and shuffle conversations
            all_conversations = conversations1 + conversations2
            random.shuffle(all_conversations)

            # Select conversations and store in session state
            st.session_state.selected_conversations = all_conversations[:2]
            st.session_state.all_conversations = all_conversations

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
                    # Move the conversation to finished list
                    st.session_state.all_conversations.remove(current_conversation)
                    # Save updated conversations back to JSON files
                    save_conversations(file1_path+"rated.json", [c for c in st.session_state.conversations1 if c not in st.session_state.all_conversations])
                    save_conversations(file2_path+"rated.json", [c for c in st.session_state.conversations2 if c not in st.session_state.all_conversations])

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
            
            # Option to download results as a CSV (only shown to administrators)
            if st.sidebar.checkbox("Show Admin Options", False):
                if st.button("Download Results"):
                    df = pd.DataFrame.from_dict(results, orient='index')
                    df.to_csv('evaluation_results.csv')
                    st.success("Results downloaded as evaluation_results.csv")
