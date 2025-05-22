"""
This is the inital training process, to be done iteratively as 
boostrapping occurs, refining the evaluation as it proceeds

"""

data = [
  {
    "agent_name": ["George Jones"],
    "agent_id": ["AG123"],
    "category": "resume",
    "upload_date": "2024-11-12",
    "text": {
    "general": "George Jones\nOperations Manager\n\nExperienced in team leadership. Led 40+ warehouse "
    "employees at LogiTrans. Initiated SOP reform, but needed supervision when working "
    "alone under stress.",
    "source": "resume"   
    }
  },
  {
    "agent_name": ["George Jones"],
    "agent_id": ["AG123"],
    "category": "feedback",
    "source": "feedback",
    "text": {
      "general": "George is a great motivator and speaks up for the team. Occasionally makes"
    " independent decisions without full consideration.",
    "feedback_date": "2025-02-01",
    "reviewer": "Martha L."
    }
  },
  {
    "agent_name": ["Sarah Lee"],
    "agent_id": ["AG107"],
    "category": "survey",
    "source": "employee_survey",
    "text": {
      "general": "Prefers individual work. Avoids group discussions. Often solves problems on "
      "her own but lacks communication when stuck.",
      "submitted": "2025-01-10"
    }
    
 
    

  },
  {
    "agent_name": ["Sarah Lee"],
    "agent_id": ["AG107"],
    "category": "resume",
    "source": "resume",
    "text": {
      "general": "Sarah Lee\nBackend Engineer\n\nWorked remotely for 3 years. Known for autonomy. "
      "Created internal APIs, but didn't participate in sprint retros or team standups "
      "consistently.",
      "upload_date": "2024-10-20"
    }
  },
  {
    "agent_name": ["John Doe"],
    "agent_id": ["AG999"],
    "category": "feedback",
    "source": "feedback",
    "text": {
        
    "general": "John brings the team together. Leads meetings and manages "
    "timelines. Sometimes seeks help on technical tasks but always follows through.",
    "quarter": "Q4-2024"
    }
    
  },
  {
    "agent_name": ["Emily Brown"],
    "agent_id": ["AG333"],
    "category": "resume",
    "source": "resume",
    "text": {
        "general": "Emily Brown\nUI/UX Designer\n\nFreelanced for 5+ startups. Comfortable "
        "working solo. Avoids team slack channels. Completed complex redesigns under tight "
        "deadlines without oversight.",
        "upload_date": "2024-12-04"
    }
  },
  {
    "agent_name": ["Emily Brown"],
    "agent_id": ["AG333"],
    "category": "survey",
    "source": "employee_survey",
    "text": {
      "feedback": "She works independently but doesn’t seek peer review. Very resourceful."
      "Prefers tools and tutorials over asking colleagues.",
      "submitted": "2025-03-22"
    }
  },
  {
    "agent_id": ["AG442"],
    "agent_name": ["Daniel Yu"],
  "category": "resume",
  "source": "C:\\Users\\Daniel\\Resumes\\daniel_yu_resume_2025.docx",
  "text": {
    "General": "Daniel Yu\n2137 Lakeside Blvd, Toronto, ON\n(416) 123-9923 | daniel.yu.dev@gmail.com\n\nI’m a software engineer with a stubborn streak for optimization. I once rewrote 4 legacy functions in my sleep. I prefer terminal windows to Slack channels.\n\nEXPERIENCE\nSoftware Developer – Wave, Toronto\n2023–2025\nBuilt internal tools no one wanted to maintain, but I loved it.\n\nEDUCATION\nB.Sc. in Computer Science, University of Waterloo\nGraduated: 2023\n",
    "skills": "C++, TypeScript, PostgreSQL, Docker, REST APIs",
    "Publications": "",
    "Notes": "Was on leave for 6 months in 2024 for travel and personal development. Volunteered teaching coding in rural BC."
    }
  },
  {
    "agent_id": ["AG811"],
    "agent_name": ["Chloe Ramirez"],
    "category": "review",
    "source": "C:\\Data\\Reviews\\feedback_batch_march2025.csv",
    "text": {
      "feedback": "Chloe is detail-oriented and handles client escalations gracefully. However, she's hesitant to delegate work and this slows down larger projects.",
      "reviewer": "Mark T.",
      "nine_box_category": "Category 4: ‘Key Contributor’ (High performance, Medium potential)",
      "person_name": "Chloe Ramirez",
      "reviewed": "true",
      "updated": "false",
      "id": "10882"
    }
  },
  {
        "agenet_id": "AG592",
        "agent_name": "Anand Singh",
    "category": "employee_survey",
    "source": "C:\\Surveys\\2025_Q1\\employee_feedback_form_Anand.txt",
    "text": {
      "summary": "Feels confident in day-to-day tasks. Prefers asynchronous communication. Avoids team meetings. Wants clearer ownership of tasks.",
      "submitted_on": "2025-02-14",
      "cooperation_score": "2",
      "self_eval": "I perform better when I know expectations clearly. I get frustrated when meetings don't have an agenda."
    }
  },
  {
    "agent_id": "AG701",
    "agent_name": "Hannah Blake",
    "category": "resume",
    "source": "C:\\Users\\Hannah\\OneDrive\\Desktop\\resume_final_final2_real.docx",
    "text": {
      "General": "Hannah Blake\nWeb Designer, 8 years exp.\nWhy am I good? I finish things. I don’t panic when figma crashes.\n\nWork:\nFreelancer 2017–2025 (no boss, no sick days)\nFrontend contract work (React mostly)\n\nSchool:\nVisual Design Diploma, OCAD University (2016)\n\nSide note: Took a break in 2020 (burnout). Worked part-time as a baker.\n\nTools: Figma, Adobe XD, React, CSS-in-JS, Sketch (but not by choice)",
      "Experience": "",
      "skills": "Design systems, user research, prototyping, stakeholder interviews",
      "extraneous": "Unrelated projects: built a game in Unity that I never shipped."
    }
  }]