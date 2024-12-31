import streamlit as st
from scrape import Scraper
from langchain_community.document_loaders import PyPDFLoader
from evaluator_agent import evaluate_resume
from chat_agent import call_chat_agent
import plotly.graph_objects as go

def on_job_text_change():
    # Delete the chat messages history to reinitialise the memory for the new job
    if "messages" in st.session_state:
        del st.session_state.messages
    if "evaluation" in st.session_state:
        del st.session_state.evaluation
    st.session_state.evaluation_area = st.empty()
def select_job(jobs: list) -> None:
    # Transform the job list for dropdown display
    transformed_jobs = [f"{job[6]} at {job[0]}" for job in jobs]

    # Create a dropdown for job selection
    selected_job = st.selectbox(
        "Select a job:", transformed_jobs, placeholder="Choose a job"
    )

    # Get the selected job index
    selected_index = transformed_jobs.index(selected_job)
    job_details = jobs[selected_index]
    st.session_state.job_text = f"""### Job title\n{job_details[6]}\n
### Company name\n{job_details[0]}\n
### Company account\n{job_details[1]}\n
### Location\n{job_details[2]}\n
### Date posted\n{job_details[3]}\n
### Number of applicants\n{job_details[4]}\n
### Skills\n{', '.join(job_details[5])}\n
### Job description\n{job_details[7]}"""
    on_job_text_change()

def create_donut_chart(score: int | float):
    fig = go.Figure(data=[go.Pie(
        values=[score, 10 - score],
        hole=0.6,
        textinfo='none',
        marker=dict(colors=["#009688", "#ECEFF1"])
    )])
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=50,
        width=50,
    )
    return fig
def display_category(name: str, details: dict) -> None:
    col1, col2, col3 = st.columns([5, 1, 1])
    with col1:
        st.markdown(f"### {name.capitalize()}")
    with col2:
        st.markdown(f"<b style='text-align: right; font-size: 32px;'>{details['score']}/10</b>", unsafe_allow_html=True)
    with col3:
        chart = create_donut_chart(details["score"])
        st.plotly_chart(chart, use_container_width=True, key=name)
    
    with st.expander("Positive Points"):
        for point in details["positive"]:
            st.write(f"- {point}")
    
    with st.expander("Negative Points"):
        if details["negative"]:
            for point in details["negative"]:
                st.write(f"- {point}")
        else:
            st.write("No negative points.")

def run_chat_agent(resume: str, job_description: str):
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system",
                "content": f"""
                You are a career advisor for a candidate with the resume delimited by <<<>>> and the job description delimited by ((( ))).
                Resume:
                <<<
                {resume}
                >>>
                Job description:
                (((
                {job_description}
                )))
                Answer the questions giving the given information only. If the candidate asks a question that you don't have an answer to, say that you don't know the answer.
                """
            }
        ]

    # Display chat messages from history on app rerun
    message_container = st.container(height=600)
    for message in st.session_state.messages:
        if message["role"]!="system":
            message_container.chat_message(message["role"]).write(message["content"])

    # Accept user input
    if prompt := st.chat_input("How can I help you?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        message_container.chat_message("user").write(prompt)

        # Display assistant response in chat message container
        stream = call_chat_agent(st.session_state.messages)
        response = message_container.chat_message("assistant").write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})


if 'scraper' not in st.session_state:
    st.session_state.scraper = Scraper()
if "job_text" not in st.session_state:
    st.session_state.job_text = " "
if "show_dropdown" not in st.session_state:
    st.session_state.show_dropdown = False

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

    st.session_state.resume_content = "\n".join(page.page_content for page in pages)
    # Display the resume content (optional)
    with st.expander("Show Resume Content"):
        st.write(st.session_state.resume_content)

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

if st.button("Search", type='primary', use_container_width=True, icon='🔍'):
    search_area = st.empty()
    with search_area.container():
        search_area.progress(20, "Searching for jobs...")
    jobs = scraper.scrape(job_title, region, date_posted, experience_level, company_name)
    
    st.session_state.jobs = jobs
    st.session_state.show_dropdown = True
    search_area.empty()

if st.session_state.get("show_dropdown", True):
    select_job(st.session_state.jobs)

# Editable text box with job details
job_text = st.text_area(
    "Job Description:", 
    st.session_state.job_text, 
    height=300,
    on_change=on_job_text_change
)

# Update the session state with edited text
st.session_state.job_text = job_text

tab1, tab2 = st.tabs(["⭐ Evaluation", "💬 Free Chat"])
with tab1:
    if st.button("Evaluate", type='primary', use_container_width=True, icon='🧐'):
        st.session_state.evaluation_area = st.empty()
        with st.session_state.evaluation_area.container():
            progress_bar = st.progress(30, "Evaluating...")
        st.session_state.evaluation = evaluate_resume(st.session_state.resume_content, st.session_state.job_text)

    if "evaluation" in st.session_state:
        with st.session_state.evaluation_area.container():
            col1, col2, col3 = st.columns([4, 2, 1])
            with col1:
                st.markdown(f"# Global Score")
            with col2:
                st.markdown(f"<b style='text-align: right; font-size: 42px;'>{float(st.session_state.evaluation["global_score"])}/10</b>", unsafe_allow_html=True)
            with col3:
                chart = create_donut_chart(float(st.session_state.evaluation["global_score"]))
                st.plotly_chart(chart, use_container_width=True, key="Global Score")
            for category, details in st.session_state.evaluation.items():
                if category != "global_score":
                    display_category(category, details)

with tab2:
    if ("resume_content" in st.session_state) and ("job_text" in st.session_state):
        run_chat_agent(st.session_state.resume_content, st.session_state.job_text)
