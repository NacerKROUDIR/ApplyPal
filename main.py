import streamlit as st
from scrape import Scraper, extract_body
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from agent import parse_with_ollama


def display_job_info(job_info):
    company_name, company_account, location, date_posted, n_applicants, skills, job_title, job_description = job_info
    
    # Create an expander for each job posting
    with st.expander(f"{job_title} at {company_name}", expanded=False):
        # Job title and company info
        st.markdown(f"**Company**: [{company_name}]({company_account})")
        st.markdown(f"**Location**: {location}")
        st.markdown(f"**Posted**: {date_posted}")
        st.markdown(f"**Number of Applicants**: {n_applicants}")
        st.markdown(f"**Skills Required**: {skills}")
        
        # Job description
        st.markdown("### Job Description")
        st.write(job_description)


if 'scraper' not in st.session_state:
    st.session_state.scraper = Scraper()

scraper = st.session_state.scraper

st.title("Job Scraper Agent")

resume = st.file_uploader("Upload your resume", type=["pdf"])

if resume is not None:
    # Save the uploaded resume temporarily
    with open("temp_resume.pdf", "wb") as f:
        f.write(resume.read())
    
    # Use PyPDFLoader to read the uploaded resume
    loader = PyPDFLoader("temp_resume.pdf")
    pages = loader.load()

    # Display the resume content (optional)
    with st.expander("Show Resume Content"):
        for i, page in enumerate(pages):
            st.write(f"Page {i + 1}:")
            st.write(page.page_content)  # Display content of each page
            st.write("---" * 20)

st.markdown("## What are the roles you are interested in?")

col1, col2 = st.columns(2)

with col1:
    job_title = st.text_input("Job Title")

with col2:
    region = st.text_input("Region")

with st.expander("Show filters"):
    col1, col2, col3 = st.columns(3)

    with col1:
        date_posted = st.selectbox(
            "Date Posted",
            options=["Any time", "Past month", "Past week", "Past 24 hours"]
        )

    with col2:
        experience_level = st.selectbox(
            "Experience Level",
            options=["Any", "Internship", "Entry level", "Associate", "Mid-senior level", "Director", "Executive"]
        )

    with col3:
        company_name = st.text_input("Company")

if st.button("Search"):
    st.write("Searching for jobs")
    jobs = scraper.scrape(job_title, region, date_posted, experience_level, company_name)
    # body = extract_body(result)

    st.session_state.jobs = jobs
    
    for job in st.session_state.jobs:
        display_job_info(job)
    
    #with st.expander("View Body Content"):
    #    st.text_area("Body Content", body, height=300)

if "body" in st.session_state:
    query = st.text_area("What do you want to parse?", key="query")

    if st.button("Ask Agent"):
        if query:
            st.write("Parsing...")

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=6000,
                chunk_overlap=0,
                separators=["\n\n", "\n", " ", ""]
            )

            chunks = text_splitter.split_text(st.session_state.body)
            print(len(chunks))

            # parsed_result = parse_with_ollama(chunks, query)
            # st.write(parsed_result)
    
