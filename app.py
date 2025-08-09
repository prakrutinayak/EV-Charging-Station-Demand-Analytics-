import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
import sqlite3

# Set page title and layout
st.set_page_config(page_title="EV Charging Dashboard", layout="wide")
st.title("🔌 EV Charging Station Demand Analytics")

# Load the dataset
@st.cache_data
def load_data():
    return pd.read_csv("merged_ev_data.csv")  # Make sure this CSV exists in the folder

df = load_data()

# Sidebar Navigation
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Go to", [
    "Dataset", 
    "Cluster Plot", 
    "Recommendations", 
    "📊 Power BI Dashboard",
    "🗄️ SQL Explorer",
    "📝 Feedback"   # ✅ Added new section
])

# Page: Dataset
if page == "Dataset":
    st.subheader("📋 Dataset Overview")
    st.dataframe(df)

# Page: Cluster Plot
elif page == "Cluster Plot":
    st.subheader("📊 Visualize EV Data by Cluster")

    plot_type = st.radio("📈 Select Plot Type", ["Scatter", "Bar Chart", "Pie Chart"])

    if plot_type == "Scatter":
        st.markdown("#### 🔹 Scatter Plot: EV Adoption vs Charging Station Count")
        fig, ax = plt.subplots()
        ax.scatter(df["EV_Adoption_Index"], df["Charging_Station_Count"], c=df["Cluster"], cmap="tab10", s=100)
        ax.set_xlabel("EV Adoption Index")
        ax.set_ylabel("Charging Station Count")
        ax.set_title("City Clusters")
        st.pyplot(fig)

    elif plot_type == "Bar Chart":
        st.markdown("#### 🔹 Bar Chart: Average EV Adoption per Cluster")
        cluster_avg = df.groupby("Cluster")["EV_Adoption_Index"].mean().reset_index()
        fig, ax = plt.subplots()
        ax.bar(cluster_avg["Cluster"], cluster_avg["EV_Adoption_Index"], color='skyblue')
        ax.set_xlabel("Cluster")
        ax.set_ylabel("Average EV Adoption Index")
        ax.set_title("Average EV Adoption per Cluster")
        st.pyplot(fig)

    elif plot_type == "Pie Chart":
        st.markdown("#### 🔹 Pie Chart: City Distribution by Cluster")
        cluster_counts = df["Cluster"].value_counts().sort_index()
        fig, ax = plt.subplots()
        ax.pie(cluster_counts, labels=cluster_counts.index, autopct='%1.1f%%', startangle=140)
        ax.set_title("City Distribution by Cluster")
        st.pyplot(fig)

# Page: Recommendations
elif page == "Recommendations":
    st.subheader("📌 Station Recommendations by City")
    st.dataframe(df[["City", "EV_Adoption_Index", "Charging_Station_Count", "EV_Station_Recommendation"]])

# Page: Power BI Dashboard
elif page == "📊 Power BI Dashboard":
    st.subheader("📈 Power BI Dashboard Preview")

    # Dashboard Screenshot Preview
    try:
        st.image("powerbi_dashboard_screenshot.png", caption="Power BI Dashboard Preview", use_container_width=True)
    except FileNotFoundError:
        st.warning("⚠️ Dashboard screenshot not found. Please add 'powerbi_dashboard_screenshot.png' to the app folder.")

    # PDF Download Button
    pdf_file = "PowerBI_Dashboard.pdf"  # Ensure the file exists in the app folder
    try:
        with open(pdf_file, "rb") as f:
            pdf_data = f.read()

        st.download_button(
            label="⬇️ Download Dashboard as PDF",
            data=pdf_data,
            file_name="EV_Charging_Dashboard.pdf",
            mime="application/pdf"
        )
    except FileNotFoundError:
        st.error(f"⚠️ Could not find PDF file: {pdf_file}")


# Page: SQL Explorer
elif page == "🗄️ SQL Explorer":
    st.subheader("🧮 Run SQL Queries on the EV Dataset")

    # Create in-memory SQLite DB and load the DataFrame
    conn = sqlite3.connect(":memory:")
    df.to_sql("ev_data", conn, index=False)

    # SQL query input
    query = st.text_area("Write your SQL query below:", 
                         "SELECT City, EV_Adoption_Index, Charging_Station_Count FROM ev_data LIMIT 5")

    if st.button("Run Query"):
        try:
            result = pd.read_sql_query(query, conn)
            st.success("✅ Query executed successfully!")
            st.dataframe(result)
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ✅ Page: Feedback
elif page == "📝 Feedback":
    st.subheader("💬 Leave Your Feedback or Notes")

    st.markdown("We'd love to hear your thoughts, suggestions, or any insights you gathered from this dashboard.")

    name = st.text_input("Your Name (Optional)")
    feedback = st.text_area("Your Feedback", placeholder="Type your feedback or suggestions here...")

    if st.button("Submit Feedback"):
        if feedback.strip() != "":
            st.success("✅ Thank you for your feedback!")

            # Save feedback to a local file
            with open("feedback.txt", "a", encoding="utf-8") as f:
                f.write(f"{name or 'Anonymous'}|||{feedback.strip()}\n")
        else:
            st.warning("⚠️ Please enter some feedback before submitting.")

    # 🔍 Display All Past Feedbacks
    st.markdown("---")
    st.subheader("📜 Previous Feedbacks")

    try:
        with open("feedback.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        if lines:
            feedback_data = [line.strip().split("|||") for line in lines if "|||" in line]
            feedback_df = pd.DataFrame(feedback_data, columns=["Name", "Feedback"])
            st.dataframe(feedback_df)
        else:
            st.info("No feedbacks submitted yet.")
    except FileNotFoundError:
        st.info("Feedback file not found. Be the first to give feedback!")