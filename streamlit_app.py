import streamlit as st
import sqlite3
from sqlite3 import Error

# Create database connection and tables
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('research_management.db')
    except Error as e:
        st.error(f"Error: {e}")
    return conn

def create_tables(conn):
    try:
        sql_create_areas_table = """CREATE TABLE IF NOT EXISTS areas (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL
                                    );"""
        sql_create_researchers_table = """CREATE TABLE IF NOT EXISTS researchers (
                                            id integer PRIMARY KEY,
                                            name text NOT NULL
                                        );"""
        sql_create_files_table = """CREATE TABLE IF NOT EXISTS files (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        areas text NOT NULL,
                                        researchers text NOT NULL,
                                        content blob NOT NULL
                                    );"""
        conn.execute(sql_create_areas_table)
        conn.execute(sql_create_researchers_table)
        conn.execute(sql_create_files_table)
    except Error as e:
        st.error(f"Error: {e}")

# Authentication function
def authenticate_user():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = None

    left, right = st.sidebar.columns(2)
    if st.session_state.authenticated is None:
        if left.button("Administrator"):
            st.session_state.authenticated = "Administrator"
        if right.button("Visitor"):
            st.session_state.authenticated = "Visitor"

        if st.session_state.authenticated == "Administrator":
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                if password == "admin":
                    st.session_state.authenticated = "Administrator"
                else:
                    st.sidebar.error("Invalid password")
                    st.session_state.authenticated = None

# Add new research area
def add_research_area(conn):
    new_area = st.text_input("Add Research Area")
    if st.button("Add Area"):
        if new_area:
            try:
                conn.execute("INSERT INTO areas (name) VALUES (?)", (new_area,))
                conn.commit()
                st.success(f"Added new area: {new_area}")
            except Error as e:
                st.error(f"Error: {e}")

# Add new researcher
def add_researcher(conn):
    new_researcher = st.text_input("Add Researcher Name")
    if st.button("Add Researcher"):
        if new_researcher:
            try:
                conn.execute("INSERT INTO researchers (name) VALUES (?)", (new_researcher,))
                conn.commit()
                st.success(f"Added new researcher: {new_researcher}")
            except Error as e:
                st.error(f"Error: {e}")

# Tag files with areas and researchers
def tag_files(conn, areas, researchers):
    selected_areas = st.multiselect("Select Research Areas", areas)
    selected_researchers = st.multiselect("Select Researchers", researchers)
    uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
    if st.button("Upload"):
        if uploaded_files:
            for uploaded_file in uploaded_files:
                try:
                    file_info = (
                        uploaded_file.name,
                        ','.join(selected_areas),
                        ','.join(selected_researchers),
                        uploaded_file.read()
                    )
                    conn.execute("INSERT INTO files (name, areas, researchers, content) VALUES (?, ?, ?, ?)", file_info)
                    conn.commit()
                    st.success(f"Uploaded file: {uploaded_file.name}")
                    st.success(f"Tagged with areas: {selected_areas}")
                    st.success(f"Tagged with researchers: {selected_researchers}")
                except Error as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please upload at least one file.")

# Display and filter uploaded files
def display_and_filter_files(conn, admin=False):
    st.header("Uploaded Files")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files")
        files = cursor.fetchall()
        if files:
            filter_area = st.multiselect("Filter by Research Areas", [row[0] for row in conn.execute("SELECT name FROM areas")])
            filter_researcher = st.multiselect("Filter by Researchers", [row[0] for row in conn.execute("SELECT name FROM researchers")])

            filtered_files = [
                file for file in files
                if (not filter_area or any(area in file[2].split(',') for area in filter_area)) and
                   (not filter_researcher or any(researcher in file[3].split(',') for researcher in filter_researcher))
            ]

            if filtered_files:
                cols = st.columns(2)
                for i, file in enumerate(filtered_files):
                    col = cols[i % 2]
                    with col:
                        with st.container():
                            st.markdown(
                                f"""
                                <div style="border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin: 10px 0;">
                                    <h3>{file[1]}</h3>
                                    <p><b>Research Areas:</b> {file[2]}</p>
                                    <p><b>Researchers:</b> {file[3]}</p>
                                </div>
                                """, unsafe_allow_html=True)

                            one, two, three = st.columns([2, 1, 1])
                            with one:
                                st.download_button("Download", file[4], file[1])
                            if admin:
                                with two:
                                    if st.button("Modify", key=f"modify_{file[0]}_btn"):
                                        st.session_state[f"modify_{file[0]}"] = True
                                with three:
                                    if st.button("Delete", key=f"delete_{file[0]}_btn"):
                                        st.session_state[f"delete_{file[0]}"] = True
                        if admin and st.session_state.get(f"modify_{file[0]}"):
                            modify_file(conn, file)
                        if admin and st.session_state.get(f"delete_{file[0]}"):
                            delete_file(conn, file[0])
                            st.experimental_rerun()
            else:
                st.info("No files match the selected filters.")
        else:
            st.info("No files uploaded yet.")
    except Error as e:
        st.error(f"Error: {e}")

# Modify a file
def modify_file(conn, file):
    st.markdown(f"### Modify File: {file[1]}")
    new_areas = st.multiselect("Modify Research Areas", [row[0] for row in conn.execute("SELECT name FROM areas")], file[2].split(','))
    new_researchers = st.multiselect("Modify Researchers", [row[0] for row in conn.execute("SELECT name FROM researchers")], file[3].split(','))
    if st.button("Save Changes", key=f"save_{file[0]}"):
        try:
            conn.execute("UPDATE files SET areas = ?, researchers = ? WHERE id = ?", (','.join(new_areas), ','.join(new_researchers), file[0]))
            conn.commit()
            st.success(f"Updated file: {file[1]}")
            st.session_state[f"modify_{file[0]}"] = False
            st.experimental_rerun()
        except Error as e:
            st.error(f"Error: {e}")

# Delete a research area
def delete_research_area(conn):
    area_to_delete = st.selectbox("Select Research Area to Delete", [row[0] for row in conn.execute("SELECT name FROM areas")])
    if st.button("Delete Area"):
        try:
            conn.execute("DELETE FROM areas WHERE name=?", (area_to_delete,))
            conn.commit()
            st.success(f"Deleted area: {area_to_delete}")
        except Error as e:
            st.error(f"Error: {e}")

# Delete a researcher
def delete_researcher(conn):
    researcher_to_delete = st.selectbox("Select Researcher to Delete", [row[0] for row in conn.execute("SELECT name FROM researchers")])
    if st.button("Delete Researcher"):
        try:
            conn.execute("DELETE FROM researchers WHERE name=?", (researcher_to_delete,))
            conn.commit()
            st.success(f"Deleted researcher: {researcher_to_delete}")
        except Error as e:
            st.error(f"Error: {e}")

# Delete a file
def delete_file(conn, file_id):
    try:
        conn.execute("DELETE FROM files WHERE id=?", (file_id,))
        conn.commit()
        st.success(f"Deleted file with ID: {file_id}")
    except Error as e:
        st.error(f"Error: {e}")

# Display available areas and researchers
def display_areas_and_researchers(conn):
    st.subheader("Available Research Areas")
    areas = [row[0] for row in conn.execute("SELECT name FROM areas")]
    if areas:
        for area in areas:
            st.markdown(f"- **{area}**")
    else:
        st.markdown("_No research areas available._")

    st.subheader("Available Researchers")
    researchers = [row[0] for row in conn.execute("SELECT name FROM researchers")]
    if researchers:
        for researcher in researchers:
            st.markdown(f"- **{researcher}**")
    else:
        st.markdown("_No researchers available._")

st.set_page_config(
    page_title="U-M Center For Ergonomics Research Hub",
    page_icon="📚",
)

# Main application
def main():
    st.title("U-M Center for Ergonomics Research Hub")

    conn = create_connection()
    if conn is not None:
        create_tables(conn)
    else:
        st.error("Error! Cannot create the database connection.")

    st.sidebar.title("Role Selection")
    authenticate_user()

    user_role = st.session_state.authenticated

    if user_role == "Administrator":
        # Display available areas and researchers
        display_areas_and_researchers(conn)
        
        st.sidebar.success("Logged in as Administrator")

        menu = ["Modify Research Area", "Modify Researcher List", "Upload Files", "Modify Files", "Add Unit"]
        choice = st.sidebar.selectbox("Select Action", menu)
        if choice == "Modify Research Area":
            st.header("Research Areas")
            add_research_area(conn)
            delete_research_area(conn)
        elif choice == "Modify Researcher List":
            st.header("Researchers")
            add_researcher(conn)
            delete_researcher(conn)
        elif choice == "Upload Files":
            st.header("Upload and Tag Files")
            areas = [row[0] for row in conn.execute("SELECT name FROM areas")]
            researchers = [row[0] for row in conn.execute("SELECT name FROM researchers")]
            tag_files(conn, areas, researchers)
        elif choice == "Modify Files":
            display_and_filter_files(conn, admin=True)
      


    elif user_role == "Visitor":
        st.sidebar.info("Logged in as Visitor")
        authenticate_user()
        # Display and filter uploaded files
        display_and_filter_files(conn)

    else:
        st.sidebar.warning("Please choose your role to access the system.")

if __name__ == "__main__":
    main()
