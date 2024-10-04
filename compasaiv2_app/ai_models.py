
def generate_roadmap(roadmap_type, scenario, path, courses, mentors, peers, project, groups, client):
    prompt = f'''
    Context:
    You are an intelligent assistant that generates personalized roadmaps for users based on their skill level, career path, and goals. Your goal is to create a roadmap for a tech enthusiast looking to start their career in {path}. You will provide the roadmap depending on the selected level either (Beginner, Intermediate, and Professional) and generate tasks, courses, and mentorship activities for each level.

    Parameters to Consider:
    - Roadmap Type: {roadmap_type}, 
    - Scenario: {scenario}
    - Path: {path}
    - Available Courses: {courses}
    - Available Mentors: {mentors}
    - Available Peers: {peers}
    - Projects: {project}
    - Groups: {groups}
    
    JSON Format:
    Your response should follow this exact JSON format:
    
    {{
            "level": "ROADMAP TYPE",
            "startdate": "YYYY-MM-DD",
            "sections": [
                {{
                    "title": "SECTION",
                    "id": 1,
                    "duration": "Duration in weeks (number only e.g 3)",
                    "startdate": "YYYY-MM-DD",
                    "progress": 0-100 (percentage)(default for SECTION ID 1 progress only should be 5),
                    "tasks": [
                        {{
                            "name": "Task Name",
                            "sub_id": 1,
                            "status": "pending/completed",
                            "description": "Brief description of the task.",
                            "action": "Action type (e.g., path_courses, community, project, roadmap, etc.)"
                        }},
                        ...
                    ]
                }},
                ...
            ]
    }}
    

    Roadmap Levels (Depending on the Roadmap Type Selected: {roadmap_type}):
    - If Beginner: Start by introducing the core skills for {path}, focusing on basic courses and initial projects.
    - If Intermediate: Progress to more advanced concepts, hands-on projects, and group work, encouraging networking.
    - If Professional: Focus on mastery, real-world projects, certifications, and job applications.
    - If Custom: Focus on scenario and provide a basic step by step guide. 

    Sections to Include:
    - INTRODUCTION: Initial courses or orientation tasks for the beginner level.
    - LEARNING: Learning tasks, projects, and assessments.
    - PRACTICE: Practical exercises, projects, or real-world applications.
    - NETWORK: Networking and mentorship sessions, peer activities.
    - CERTIFICATION: Any assessments, certificates, or proof of skill mastery.

    Tasks:
    Each section will contain tasks. Select tasks from the following:
    - Take a Course: "path_courses"
    - Make a Post: "community"
    - Work on Project: "project"
    - Apply to Job: "roadmap"
    - Take Assessments: "messages"
    - Network: "connect_mentors"
    - Join Focus Groups: "messages"
    - Join Office Hours: "messages"
    - Set up Portfolio: "profile"

    Expected Outcome:
    Generate a roadmap for a user who is a {scenario} with the selected career path: {path}.
    '''
    
    result_message = [{
                            "role": "system", 
                            "content":  f"{prompt}" 
                            }]
    result_completion = client.chat.completions.create(
                model='gpt-35-turbo',
                messages=result_message,
                temperature=0.7,
                
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
    result = result_completion.choices[0].message.content
   
    return result


def generate_summary(client, profile, info):
    summary_message = [{
        "role": "system", 
        "content": f'''
            Context
            --------
            You are an expert AI psychometrist who summarizes user profile information about their personality, strengths, academic background, resources and motivation. This summary needs to elavate & highlight key information that would be helpful choosing a career in tech.
            
            Task
            --------
            1. Using the listed rules below, summarise the user's psychometric traits.
            2. Use the below parameters as information for the summary
            3. Only Highlight key information that can steer the path of user's career, good or bad. 
            4. Personalise the summary by using user's name that will be provided in the parameter

            
            Parameters
            ---------
            - User's name is {profile.display_name}
            - Question: What are your existing tech skills.  Answer: {info.skills}
            - Question: How many hours a week? Weekly availability to learn and practice. Answer: {info.hours}
            - Question: Which resources can you have access to? Answer: {info.resources}
            - Question: How proficient are you with computers? Answer: {info.computers}
            - Question: What are your top strengths? Answer: {info.strengths}
            - Question: What are your top weaknesses? Answer: {info.weakness}
            - Question: Do you prefer working in a team or alone? Answer: {info.team}
            - Question: Tell me about how you spend your free time. Answer: {info.interests}
            - Question: Tell me about your academic background. Answer: {info.academics}
            - Question: Do you have any prior exposure to technology? {info.exposure}
            - Question: ⁠What is your motivation to acquire a tech skill? {info.motivation}


            Rules
            --------
            * Address user by name.
            * The summary must contain key information that can help user's career decision. 
            * The entire comment should be 50 words or less
            * The entire comment should be a single paragraph only.
            * The entire comment should be WORDS or NUMBERS only, no special characters.
            * The output should just be the summary no titles, headers , dictionaries, lists. Just the summary.
            * Do not give any advice, just summarise. 
            

        '''
    }]

    summary_completion = client.chat.completions.create(
            model='gpt-35-turbo',
            messages=summary_message,
            temperature=0.7,
    
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
    summary = summary_completion.choices[0].message.content
    return summary

def generate_recommendation(client, profile, info, fields):
    recommendation_message = [{
            "role": "system", 
            "content": f'''
                Context
                --------
                You are an expert AI psychometrist recommender who recommends tech skills that fit the user's psychometric summary. The summary contains user profile information about their personality, strengths, academic background, resources, and motivation. This summary will be used to choose possible careers in tech for the user.
                
                Task
                --------
                1. Using the listed rules below, recommend the top 3 tech skills that fit the user's information listed in the below parameters
                2. Choose the top 3 recommended skills from the provided Skills List only; do not change any words.
                3. Provide a reason each recommended skill fits the user.
                4. Personalise the reason by using user's name.

                Parameters
                ---------
                - User's name is {profile.display_name}
                - Question: What are your existing tech skills.  Answer: {info.skills}
                - Question: How many hours a week? Weekly availability to learn and practice. Answer: {info.hours}
                - Question: Which resources can you have access to? Answer: {info.resources}
                - Question: How proficient are you with computers? Answer: {info.computers}
                - Question: What are your top strengths? Answer: {info.strengths}
                - Question: What are your top weaknesses? Answer: {info.weakness}
                - Question: Do you prefer working in a team or alone? Answer: {info.team}
                - Question: Tell me about how you spend your free time. Answer: {info.interests}
                - Question: Tell me about your academic background. Answer: {info.academics}
                - Question: Do you have any prior exposure to technology? {info.exposure}
                - Question: ⁠What is your motivation to acquire a tech skill? {info.motivation}

                Skills List
                ---------
                Below is the list of skills to choose from. ONLY CHOOSE FROM THIS LIST AND RETURN THE EXACT WORD. 
                {fields}

                Decision Factors
                --------------
                The factors below are ranked according to importance in the recommendation decision process. The top-ranked factors should be considered first using the corresponding percentage of importance.
                - Existing Skills  - 25%
                - Academic Background - 20%
                - Available Time and Resources -15%
                - Computer Exposure and Proficiency - 10%
                - Interests and Motivation - 15%
                - Strengths & Weaknesses - 10%
                - Working in a Team - 5%

                Rules
                --------
                * Select only 3 of the most fitting tech skills for the user's psychometric traits.
                * Use the top-ranking factors to make a decision about the recommendations.
                * Choose the top 3 recommendations from the Skills List above ONLY.
                * Return output in the JSON format specified below.
                * Reason for each skill should be 20 words or less
                * Personalise the reason by using user's name.

                Output Format
                --------
                Your response should be in the following JSON format:

                [
                    {{
                        "ID": <ID>,
                        "skill": "<skill>",
                        "reason": "<reason>"
                    }},
                    {{
                        "ID": <ID>,
                        "skill": "<skill>",
                        "reason": "<reason>"
                    }},
                    {{
                        "ID": <ID>,
                        "skill": "<skill>",
                        "reason": "<reason>"
                    }}
                ]
            '''
        }]

    recommendation_completion = client.chat.completions.create(
            model='gpt-35-turbo',
            messages=recommendation_message,
            temperature=0.7,
       
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
    recommendation = recommendation_completion.choices[0].message.content
   
    return recommendation


def get_mentor_info(pdf_text, client):
    # Template for the extracted information
    template = {
        "about": "", 
        "linkedin": "", 
        "skills": [], 
        "education": [], 
        "experience": [], 
        "path": ""
    }

    # Define career fields for "Path" selection
    career_fields = [
        "Graphics Design","Web Design","Motion Graphics","Animation","Video Editing",
        "Content Writing","Content Creation","Product Design","Product Management",
        "Scrum Management","Product Marketing","Business Analysis","Business Intelligence",
        "Business Analytics","Business Development","Financial Analysis","Legal and Compliance",
        "Customer Relationship Management (CRM)","Digital Marketing","Content Marketing",
        "Public Relations (PR)","Community Management","Game Development","Mobile App Development",
        "Database Management","Frontend Development","Backend Development","Fullstack Development",
        "Blockchain Development","Trading Algorithm Development","Quality Assurance",
        "Cloud & DevOps","Cybersecurity","Data Analysis","Data Analytics","Data Science",
        "Data Engineering","Artificial Intelligence","Project Management","IT Administration",
        "Customer Support","Virtual Assistant"
    ]

    # Construct the prompt for GPT-4
    prompt = f'''
        Context:
        You are an intelligent assistant designed to extract information from resumes to help populate a mentor profile for a tech career platform.

        Task:
        1. Extract the following information from the resume text provided.
        2. Choose the most appropriate career path for mentoring based on the skills and experience listed in the resume. Use exact words from the career fields list provided.

        Resume Text:
        {pdf_text}

        Parameters to Extract:
        ----------------------
        1. "about": Extract the summary information about the mentor.
        2. "linkedin": Extract the LinkedIn URL if available.
        3. "skills": Extract the top skills listed.
        4. "education": Extract education details in the following format:
            [
                {{"id": 1, "school": "School Name", "degree": "Degree", "start_date_raw": "YYYY-MM-DD", "end_date_raw": "YYYY-MM-DD", "start_date": "MMM YYYY", "end_date": "MMM YYYY"}}
            ]
        5. "experience": Extract work experience details in the following format:
            [
                {{"id": 1, "title": "Job Title", "company": "Company Name", "description": "Description", "start_date_raw": "YYYY-MM-DD", "end_date_raw": "YYYY-MM-DD", "start_date": "MMM YYYY", "end_date": "MMM YYYY"}}
            ]
        6. For both education and experience, if the end date is "Present", leave the end date fields ("end_date_raw" and "end_date") blank.
        7. "path": Based on the resume information, mention 1 skill from the following pool of skills that fits the mentor mostly to mentor people as the "Path" field:
            {career_fields}

        JSON Format:
        Return the extracted information as a JSON object following the format below:
        {{
            "about": "Summary about the mentor.",
            "linkedin": "LinkedIn URL",
            "skills": ["Skill 1", "Skill 2", ...],
            "education": [
                {{"id": 1, "school": "School Name", "degree": "Degree", "start_date_raw": "YYYY-MM-DD", "end_date_raw": "YYYY-MM-DD", "start_date": "MMM YYYY", "end_date": "MMM YYYY"}}
            ],
            "experience": [
                {{"id": 1, "title": "Job Title", "company": "Company Name", "description": "Description", "start_date_raw": "YYYY-MM-DD", "end_date_raw": "YYYY-MM-DD", "start_date": "MMM YYYY", "end_date": "MMM YYYY"}}
            ],
            "path": "Selected career path from the provided career fields"
        }}
    '''

    summary_message = [{
                            "role": "system", 
                            "content":  f"{prompt}" 
                            }]
    summary_completion = client.chat.completions.create(
                model='gpt-35-turbo',
                messages=summary_message,
                temperature=0.7,
              
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
    summary = summary_completion.choices[0].message.content
   
    return summary



def assistant_response(client, history,  user_question, user_profile, available_mentors,available_projects, available_courses, skills, tasks ):
    prompt = f"""
    You are a smart AI assistant for a tech platform that helps users navigate and make decisions about their career growth. Your role is to assist users based on their queries, providing appropriate guidance only when requested. Be conversational and helpful, but avoid overwhelming the user with unnecessary details unless directly relevant to their question.

    The user has asked the following question: "{user_question}"

    The user profile contains the following information:
    - Current Skill Level: {user_profile['skill_level']}
    - Interests: {', '.join(user_profile['interests'])}
    - Ongoing Courses: {', '.join(user_profile['ongoing_courses'])}
    - Completed Projects: {', '.join(user_profile['completed_projects'])}

    Conversation History: {history}

    Available Mentors:
    {', '.join([mentor['name'] + " (" + mentor['specialty'] + ")" for mentor in available_mentors])}

    Available Projects:
    {', '.join([project['name'] for project in available_projects])}

    Available Courses:
    {', '.join([course['name'] for course in available_courses])}

    Available Skills:
    {', '.join([skill['name'] for skill in skills])}

    Tasks:
    {', '.join([task['name'] for task in tasks])}

    Your job is to answer the user's question **only** when it's specifically asking about a mentor, course, project, or any other resource. If the user's question is a greeting or something general, respond in a friendly manner without offering specific resources unless the user explicitly requests them.

    Guidelines for Responses:
    
    1. **Greetings and General Responses**:
        - If the user greets you with "Hello", "Hi", or something similar, simply respond with a warm greeting, without diving into recommendations unless requested.
        - Example response: "Hello! How can I assist you today?"

    2. **Mentor Search**:
        - If the user asks "Who is the best mentor for {user_profile['interests'][0]}?", suggest a mentor based on their interests or current skill level.
        - Example response: "The best mentor for {user_profile['interests'][0]} is {available_mentors[0]['name']}, who specializes in {available_mentors[0]['specialty']}."

    3. **Skill Recommendation**:
        - If the user asks "What skills should I focus on?", suggest a skill based on their interests and completed projects.
        - Example response: "Since you are interested in {user_profile['interests'][0]}, I recommend focusing on the skill '{skills[0]['name']}'."

    4. **Course Search**:
        - If the user asks "What course should I take?", recommend a course based on their interests and ongoing projects.
        - Example response: "I recommend taking the {available_courses[0]['name']} course, as it aligns with your current interest in {user_profile['interests'][0]}."

    5. **General Tasks**:
        - If the user asks "What can I do now?", suggest general tasks such as projects, course activities, or mentorship.
        - Example response: "You can work on {tasks[0]['name']} to apply your skills, or reach out to {available_mentors[0]['name']} for mentorship."

    6. **Create Project Info**:
        - If the user asks "What project should I work on?", suggest a project based on their skill level and interests.
        - Example response: "You can work on the project {available_projects[0]['name']}, which aligns with your current interest in {user_profile['interests'][0]}."

    7. **Ambiguous or General Questions**:
        - If the user asks a general or ambiguous question, like "How do I start?", "What can I do?", or "Where do I begin?", respond by guiding them to explore general resources or start with basic actions (e.g., roadmap, courses).
        - Example response: "To start, you can check out your roadmap or begin with an introductory course on {available_courses[0]['name']}."

    **Rules**:
    - Provide your responses only based on the specific question the user asks.
    - If the question is general or vague, be friendly but avoid providing specific resource recommendations unless directly requested.
    - Keep your response short, concise, and personalized to the user's current situation, but only provide actionable details when asked.
    - Avoid suggesting multiple options if the user doesn't ask for them; stick to one actionable recommendation.
    - Always carry the conversation forward in a helpful, warm, and conversational tone.
    """



    summary_message = [{
                            "role": "system", 
                            "content":  f"{prompt}" 
                            }]
    summary_completion = client.chat.completions.create(
                model='gpt-35-turbo',
                messages=summary_message,
                temperature=0.7,
              
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
    summary = summary_completion.choices[0].message.content
   
    return summary
