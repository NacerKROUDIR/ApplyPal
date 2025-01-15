from langchain_openai import ChatOpenAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(temperature=0, model="gpt-4")

skills_schema = ResponseSchema(
    name="skills",
    description="Evaluate how well the candidate's skills align with the job requirements. "
                "Output a relevance score between 0 and 10. Provide the matched skills in a Python list "
                "under 'positive' and the missing skills in a Python list under 'negative'."
)

experience_schema = ResponseSchema(
    name="experience",
    description="Evaluate the relevance of the candidate's professional experience to the job requirements. "
                "Output a relevance score between 0 and 10. Provide a description of relevant experience "
                "under 'positive' and a description of missing or inadequate experience under 'negative'."
)

education_schema = ResponseSchema(
    name="education",
    description="Evaluate how well the candidate's educational background matches the job requirements. "
                "Output a relevance score between 0 and 10. Provide a description of matching qualifications "
                "under 'positive' and missing qualifications under 'negative'."
)

soft_skills_schema = ResponseSchema(
    name="soft_skills",
    description="Evaluate any additional relevant aspects, such as certifications, languages, or cultural fit. "
                "Output a relevance score between 0 and 10. Provide a description of relevant attributes "
                "under 'positive' and any missing or insufficient aspects under 'negative'."
)

global_score_schema = ResponseSchema(
    name="global_score",
    description="Calculate a weighted global score between 0 and 10 by applying the following weights: "
                "Skills (40%), Experience (30%), Education (20%), Soft Skills (10%)."
)

title_schema = ResponseSchema(
    name="title",
    description="The job title and company name. Format: 'job_title at company'."
)


response_schemas = [skills_schema, 
                    experience_schema,
                    education_schema,
                    soft_skills_schema,
                    global_score_schema,
                    title_schema,
                    ]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()
template=(
        """Evaluate the relevance of the following resume to the job description
           and provide detailed feedback\n
           Resume: {resume}\n\n
           Job Description: {job_description}\n\n
           {format_instructions}\nreturn the json only without additional paragraphs"""
    )
prompt = ChatPromptTemplate.from_template(template=template)

def evaluate_resume(resume: str, job_description: str)-> dict:
    messages = prompt.format_messages(resume=resume, 
                                      job_description=job_description,
                                      format_instructions=format_instructions
                                      )
    response = llm.invoke(messages)
    output_dict = output_parser.parse(response.content)
    return output_dict