import os
import streamlit as st
from utils.anthropic_client import call_claude, call_claude_quote  # your API call function
import base64

# Read credentials from environment variables
APP_USERNAME = os.getenv("APP_USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def login():
    st.title("Please log in")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

        if submitted:
            if username == APP_USERNAME and password == APP_PASSWORD:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password")

def main_app():
    # Sidebar menu
    page = st.sidebar.selectbox("Select a task for AI Assistant", ["Report Generator", "Quotation Generator"])

    # Page: Report Generator
    if page == "Report Generator":
        st.title('📋 Report Generator')

        # Short summary
        overall_summary = st.text_input("Overall Summary of the Day", max_chars=1000)

        # Fixed list of children
        children_names = [
            "Alice", 
            "Ben"
        ]

        # Collect activities per child
        children_activities = {}
        for name in children_names:
            st.subheader(f"{name}")
            selected_activities = st.text_input(
                f"Describe {name}'s participation",
                max_chars=100,
                key=f"activities_{name}"
            )
            children_activities[name] = selected_activities

        st.write("")

        # Validation before submit
        if st.button("Generate Report"):
            # Check if overall summary is empty
            if not overall_summary.strip():
                st.error("Please enter the Overall Summary before generating the report.")
            else:
                # Prepare the input text to send to Claude
                # You can format it nicely combining summary + activities
                user_text = f"Overall Summary:\n{overall_summary}\n\nChildren Activities:\n"
                for name, activities in children_activities.items():
                    if activities:
                        user_text += f"{name}:\nActivities: {activities}\n\n"
                
                # Call the Anthropic API
                with st.spinner("Generating report..."):
                    report = call_claude(user_text)
                
                # Show the returned report
                st.success("Report Generated!")
                st.header("📋 Generated Report")

                # Loop through each TextBlock and display the text
                for block in report:
                    st.markdown(block.text)

    # Page: Quotation Generator
    elif page == "Quotation Generator":
        st.title("💬 Quotation Generator")

        # 1: Input: Image Upload
        uploaded_file = st.file_uploader("Upload a photo of the child", type=["png", "jpg", "jpeg"])

        # Convert uploaded image to base64
        image_base64 = None
        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            image_base64 = base64.b64encode(bytes_data).decode('utf-8')
            st.success("Image uploaded and converted to Base64!")

        # 2: Teacher fills in extra info
        st.header("Child Focus Information")
        child_focus_name = st.text_input("Child's Name to Focus On")
        child_activity = st.text_input("What is the child doing?")
        child_feeling = st.text_input("Describe the child's mood or feeling (e.g., happy, proud, curious)")

        if "quotes" not in st.session_state:
            st.session_state.quotes = []  # list of dicts with keys: name, quote, image_base64

        st.write("")

        # After generating the quote:
        if st.button("Generate Quote"):
            if not child_focus_name:
                st.error("Please enter the child's name to focus on.")
            elif not child_activity:
                st.error("Please enter what the child is doing.")
            elif not child_feeling:
                st.error("Please describe the child's feeling.")
            elif not uploaded_file:
                st.error("Please upload an image.")
            else:
                with st.spinner("Generating a beautiful quote..."):
                    quote = call_claude_quote(
                        base64_image=image_base64,
                        child_focus_name=child_focus_name,
                        child_activity=child_activity,
                        child_feeling=child_feeling
                    )
                st.success("Quote Generated!")

                # Store the result
                st.session_state.quotes.append({
                    "child_name": child_focus_name,
                    "activity": child_activity,
                    "feeling": child_feeling,
                    "quote": quote,
                    "image": image_base64
                })

        # Assuming `quote` is a list of TextBlock objects
        for entry in st.session_state.quotes:
            st.markdown(f"### ✨ Quote for {entry['child_name']}:")
            # If quote is a list of TextBlocks
            for block in entry['quote']:
                st.markdown(block.text)
            
            # Display image
            image_bytes = base64.b64decode(entry['image'])
            st.image(image_bytes, use_container_width=True)
            st.markdown("---")

if not st.session_state["logged_in"]:
    login()
else:
    main_app()