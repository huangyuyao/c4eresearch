import streamlit as st

# Simulated authentication (for demonstration purposes)
def authenticate_user():
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "admin" and password == "admin":
            return "Administrator"
        else:
            return "Visitor"
    return None

# Add new research area
def add_research_area(areas):
    new_area = st.text_input("Add Research Area")
    if st.button("Add Area"):
        if new_area and new_area not in areas:
            areas.append(new_area)
            st.success(f"Added new area: {new_area}")
    return areas

# Add new researcher
def add_researcher(researchers):
    new_researcher = st.text_input("Add Researcher Name")
    if st.button("Add Researcher"):
        if new_researcher and new_researcher not in researchers:
            researchers.append(new_researcher)
            st.success(f"Added new researcher: {new_researcher}")
    return researchers

# Main application
def main():
    st.title("Research Management System")

    user_role = authenticate_user()

    if user_role == "Administrator":
        st.sidebar.success("Logged in as Administrator")
        
        # Research areas management
        st.header("Research Areas")
        research_areas = ["Cognitive", "Physical", "Other"]
        research_areas = add_research_area(research_areas)
        st.subheader("Available Research Areas")
        st.write(research_areas)

        # Researchers management
        st.header("Researchers")
        researchers = ["Yili Liu"]
        researchers = add_researcher(researchers)
        st.subheader("Available Researchers")
        st.write(researchers)

        # File upload
        st.header("Upload Files")
        uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.write("Uploaded file:", uploaded_file.name)

    elif user_role == "Visitor":
        st.sidebar.info("Logged in as Visitor")
        st.header("Research Areas")
        st.write(["Cognitive", "Physical", "Other"])

        st.header("Researchers")
        st.write(["Yili Liu"])

        st.header("Upload Files")
        st.info("File upload is available for administrators only.")

    else:
        st.sidebar.warning("Please log in to access the system.")

if __name__ == "__main__":
    main()
