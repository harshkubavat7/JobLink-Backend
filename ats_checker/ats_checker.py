


# import PyPDF2
# import re
# import json
# import sys
# from sentence_transformers import SentenceTransformer, util

# # ---------------- CONFIG ---------------- #

# TECH_SKILLS = [
#     "C","C++","Java","Python","JavaScript","TypeScript","Go","Rust","PHP","Ruby","Kotlin","Swift","Assembly Language","Bash","HTML","CSS","SQL","NoSQL","Data Structures","Algorithms","Object Oriented Programming","Operating Systems","Computer Networks","Database Management Systems","Compiler Design","Computer Architecture","Microprocessors","Microcontrollers","Embedded Systems","Digital Logic Design","VLSI Design","Verilog","VHDL","FPGA","ARM Architecture","x86 Architecture","IoT","Robotics","Sensors","Actuators","Real Time Operating Systems","Linux","Unix","Windows Internals","Shell Scripting","Git","GitHub","GitLab","Docker","Kubernetes","Jenkins","CI/CD","DevOps","Cloud Computing","AWS","Azure","Google Cloud","Virtualization","VMware","Hyper-V","OpenStack","Networking Protocols","TCP/IP","HTTP","HTTPS","FTP","DNS","DHCP","REST API","GraphQL","Web Development","Frontend Development","Backend Development","Full Stack Development","React","Angular","Vue.js","Next.js","Node.js","Express.js","Spring Boot","Django","Flask","FastAPI",".NET","ASP.NET","Microservices","Monolithic Architecture","Software Engineering","SDLC","Agile","Scrum","Kanban","Testing","Unit Testing","Integration Testing","Selenium","Cypress","Jest","Cyber Security","Cryptography","Network Security","Ethical Hacking","Penetration Testing","Firewalls","IDS","IPS","Blockchain","Smart Contracts","Ethereum","Solidity","Web3","Artificial Intelligence","Machine Learning","Deep Learning","Neural Networks","NLP","Computer Vision","Data Science","Big Data","Hadoop","Spark","Data Analytics","Business Intelligence","Power BI","Tableau","Memory Management","Process Scheduling","Deadlocks","Distributed Systems","Parallel Computing","High Performance Computing","CUDA","OpenMP","MPI","Software Defined Networking","SDN","Network Function Virtualization","NFV","Edge Computing","Quantum Computing","AR","VR","Game Development","Unity","Unreal Engine","Mobile App Development","Android Development","iOS Development","Flutter","React Native","Cross Platform Development","API Development","System Design","Scalability","Load Balancing","Caching","Message Queues","Kafka","RabbitMQ","MQTT"
# ]

# WEIGHTS = {
#     "skills": 0.5,
#     "experience": 0.3,
#     "projects": 0.2
# }

# model = SentenceTransformer("all-MiniLM-L6-v2")

# # ---------------- HELPERS ---------------- #

# def extract_text_from_pdf(path):
#     text = ""
#     with open(path, "rb") as f:
#         reader = PyPDF2.PdfReader(f)
#         for page in reader.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#     return text.lower()


# def clean_text(text):
#     return re.sub(r"[^a-z0-9\s]", " ", text)


# def extract_sections(text):
#     sections = {"skills": "", "experience": "", "projects": ""}
#     current = None

#     for line in text.split("\n"):
#         if "skill" in line:
#             current = "skills"
#         elif "experience" in line:
#             current = "experience"
#         elif "project" in line:
#             current = "projects"
#         elif current:
#             sections[current] += line + " "

#     return sections


# def extract_skills(text):
#     found = set()
#     for skill in TECH_SKILLS:
#         if skill in text:
#             found.add(skill)
#     return list(found)


# def semantic_score(a, b):
#     if not a or not b:
#         return 0.0
#     emb_a = model.encode(a, convert_to_tensor=True)
#     emb_b = model.encode(b, convert_to_tensor=True)
#     return util.cos_sim(emb_a, emb_b).item()

# # ---------------- MAIN ATS LOGIC ---------------- #

# def analyze_resume(resume_text, job_description):
#     resume_text = clean_text(resume_text)
#     job_description = clean_text(job_description)

#     sections = extract_sections(resume_text)

#     resume_skills = extract_skills(sections["skills"])
#     job_skills = extract_skills(job_description)

#     # Skill match score
#     skill_match = (
#         len(set(resume_skills) & set(job_skills)) / max(len(job_skills), 1)
#     )

#     # Semantic scores
#     experience_score = semantic_score(sections["experience"], job_description)
#     project_score = semantic_score(sections["projects"], job_description)

#     final_score = (
#         skill_match * WEIGHTS["skills"]
#         + experience_score * WEIGHTS["experience"]
#         + project_score * WEIGHTS["projects"]
#     )

#     return {
#         "ats_score": round(final_score * 100, 2),
#         "matched_skills": list(set(resume_skills) & set(job_skills)),
#         "missing_skills": list(set(job_skills) - set(resume_skills)),
#         "experience_match": round(experience_score * 100, 2),
#         "project_match": round(project_score * 100, 2),
#         "recommendation": (
#             "Strong match"
#             if final_score >= 0.7
#             else "Moderate match"
#             if final_score >= 0.4
#             else "Low match"
#         )
#     }

# # ---------------- CLI ENTRY ---------------- #

# if __name__ == "__main__":
#     try:
#         resume_path = sys.argv[1]
#         job_description = sys.stdin.read()

#         resume_text = extract_text_from_pdf(resume_path)
#         result = analyze_resume(resume_text, job_description)

#         print(json.dumps(result))
#     except Exception as e:
#         print(json.dumps({"error": str(e)}))


import PyPDF2
import re
import json
import sys
from sentence_transformers import SentenceTransformer, util

# ---------------- CONFIG ---------------- #

WEIGHTS = {
    "skills": 0.5,
    "experience": 0.3,
    "projects": 0.2
}

# Skill normalization map (REAL ATS STYLE)
SKILL_ALIASES = {
    "react": ["react", "reactjs", "react.js"],
    "javascript": ["javascript", "js"],
    "html": ["html"],
    "css": ["css"],
    "node": ["node", "nodejs", "node.js"],
    "express": ["express", "expressjs"],
    "mongodb": ["mongodb", "mongo"],
    "sql": ["sql", "mysql", "postgresql"],
    "nosql": ["nosql"],
    "rest api": ["rest api", "api", "apis"],
    "git": ["git", "github"],
    "docker": ["docker"],
    "aws": ["aws", "amazon web services"],
    "kubernetes": ["kubernetes", "k8s"],
    "python": ["python", "py"],
    
}

model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------- HELPERS ---------------- #

def extract_text_from_pdf(path):
    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.lower()


def clean_text(text):
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())


def extract_sections(text):
    sections = {"skills": "", "experience": "", "projects": ""}
    current = None

    for line in text.split("\n"):
        line = line.strip()
        if "skill" in line:
            current = "skills"
        elif "experience" in line:
            current = "experience"
        elif "project" in line:
            current = "projects"
        elif current:
            sections[current] += line + " "

    return sections


def extract_skills(text):
    found = set()
    for canonical, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            if re.search(rf"\b{re.escape(alias)}\b", text):
                found.add(canonical)
                break
    return list(found)


def semantic_score(a, b):
    if not a or not b:
        return 0.0
    emb_a = model.encode(a, convert_to_tensor=True)
    emb_b = model.encode(b, convert_to_tensor=True)
    return util.cos_sim(emb_a, emb_b).item()

# ---------------- MAIN ATS LOGIC ---------------- #

def analyze_resume(resume_text, job_description):
    resume_text = clean_text(resume_text)
    job_description = clean_text(job_description)

    sections = extract_sections(resume_text)

    resume_skills = extract_skills(sections["skills"])
    job_skills = extract_skills(job_description)

    # Skill match score
    skill_match = (
        len(set(resume_skills) & set(job_skills)) / max(len(job_skills), 1)
    )

    # Semantic similarity
    experience_score = semantic_score(sections["experience"], job_description)
    project_score = semantic_score(sections["projects"], job_description)

    final_score = (
        skill_match * WEIGHTS["skills"]
        + experience_score * WEIGHTS["experience"]
        + project_score * WEIGHTS["projects"]
    )

    return {
        "ats_score": round(final_score * 100, 2),
        "matched_skills": list(set(resume_skills) & set(job_skills)),
        "missing_skills": list(set(job_skills) - set(resume_skills)),
        "experience_match": round(experience_score * 100, 2),
        "project_match": round(project_score * 100, 2),
        "recommendation": (
            "Strong match"
            if final_score >= 0.7
            else "Moderate match"
            if final_score >= 0.4
            else "Low match"
        )
    }

# ---------------- CLI ENTRY ---------------- #

if __name__ == "__main__":
    try:
        resume_path = sys.argv[1]
        job_description = sys.stdin.read()

        resume_text = extract_text_from_pdf(resume_path)
        result = analyze_resume(resume_text, job_description)

        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
