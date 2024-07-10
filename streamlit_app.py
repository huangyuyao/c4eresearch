import streamlit as st

# Simulated authentication (for demonstration purposes)
def authenticate_user():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = None

    user_role = st.sidebar.selectbox("Choose your role", ["Visitor", "Administrator"])
    if user_role == "Administrator":
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if password == "admin":
                st.session_state.authenticated = "Administrator"
            else:
                st.sidebar.error("Invalid password")
                st.session_state.authenticated = None
    else:
        st.session_state.authenticated = "Visitor"

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

# Tag files with areas and researchers
def tag_files(areas, researchers):
    selected_areas = st.multiselect("Select Research Areas", areas)
    selected_researchers = st.multiselect("Select Researchers", researchers)
    uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
    if st.button("Upload"):
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.write(f"Uploaded file: {uploaded_file.name}")
                st.write(f"Tagged with areas: {selected_areas}")
                st.write(f"Tagged with researchers: {selected_researchers}")
        else:
            st.warning("Please upload at least one file.")

# Main application
def main():
    st.title("Research Management System")

    authenticate_user()

    user_role = st.session_state.authenticated

    if user_role == "Administrator":
        st.sidebar.success("Logged in as Administrator")
        
        # Research areas management
        st.header("Research Areas")
        if "research_areas" not in st.session_state:
            st.session_state.research_areas = ["Cognitive", "Physical", "Other"]
        research_areas = add_research_area(st.session_state.research_areas)
        st.session_state.research_areas = research_areas
        st.subheader("Available Research Areas")
        st.write(st.session_state.research_areas)

        # Researchers management
        st.header("Researchers")
        if "researchers" not in st.session_state:
            st.session_state.researchers = ["Yili Liu"]
        researchers = add_researcher(st.session_state.researchers)
        st.session_state.researchers = researchers
        st.subheader("Available Researchers")
        st.write(st.session_state.researchers)

        # File upload with tagging
        st.header("Upload and Tag Files")
        tag_files(st.session_state.research_areas, st.session_state.researchers)

    elif user_role == "Visitor":
        st.sidebar.info("Logged in as Visitor")
        st.header("Research Areas")
        st.write(["Cognitive", "Physical", "Other"])

        st.header("Researchers")
        st.write(["Yili Liu"])

        st.header("Upload and Tag Files")
        st.info("File upload and tagging is available for administrators only.")

    else:
        st.sidebar.warning("Please choose your role to access the system.")

if __name__ == "__main__":
    main()
