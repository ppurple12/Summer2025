'''
In this module, each document identifies the agents to be evaluated
the data is preprocessed to remove unnecessary noise
'''
import pprint as pp
import spacy
import re
from data.LoadingPipeline import load_all_files
from pprint import pprint
from rapidfuzz import fuzz

# loading NLP 
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 4_000_000  

#trying regular name recognition - probably wont use
def extract_agents(data, category, agent_list=None, id_list = None):
      agents_detected = []
      if agent_list and id_list:
        # If it's a resume, detect only one agent
        if category == "resume":
            for agent, agent_id in zip(agent_list, id_list):
                if agent and agent in data:  
                    agents_detected.append({"name": agent, "id": agent_id})
                    break  # stop after detecting the first agent 
        else:
            # look for all agents in the text
            for agent, agent_id in zip(agent_list, id_list):
                if agent and agent in data:  
                    agents_detected.append({"name": agent, "id": agent_id})
                elif agent_id and re.search(rf"\b{re.escape(str(agent_id))}\b", data):
                    agents_detected.append({"name": agent, "id": agent_id})
        if not agents_detected and agent_list:
            doc = nlp(data)
            for ent in doc.ents:
                if ent.label_ == "PERSON" and ent.text in agent_list:
                    # use the agent's ID if available
                    index = agent_list.index(ent.text)
                    agents_detected.append({"name": ent.text, "id": id_list[index]})

    

        # Return the agents detected
        return agents_detected

#trying NLP to get names   



def detect_agents_ner(text, agents_list=None, id_list=None, fuzzy_threshold=85):
    doc = nlp(text)
    detected_names = []
    detected_ids = []
    seen_ids = set()
    text_tokens = set(text.split())

    # Normalize the text for matching
    text_lower = text.lower()

    # 1. Use spaCy NER (exact + fuzzy match on named entities)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            ent_text = ent.text.strip()
            for name, agent_id in zip(agents_list, id_list):
                if not name or agent_id in seen_ids:
                    continue  # Skip invalid or previously seen agents

                name_lower = name.lower()

                # Exact match on entity
                if re.search(rf"\b{re.escape(name)}\b", ent_text, re.IGNORECASE):
                    detected_names.append(name)
                    detected_ids.append(agent_id)
                    seen_ids.add(agent_id)
                else:
                    # Fuzzy match on entity, but only if name is in agents_list
                    similarity = fuzz.token_set_ratio(ent_text.lower(), name_lower)
                    if similarity >= fuzzy_threshold and name in agents_list:
                        detected_names.append(name)
                        detected_ids.append(agent_id)
                        seen_ids.add(agent_id)

    # 2. Match agent ID as a literal token in the text
    for name, agent_id in zip(agents_list, id_list):
        if agent_id and str(agent_id) in text_tokens and agent_id not in seen_ids:
            detected_names.append(name)
            detected_ids.append(agent_id)
            seen_ids.add(agent_id)

    # 3. Fuzzy match full name against full document (fallback)
    for name, agent_id in zip(agents_list, id_list):
        if not name or name == "FALSE" or agent_id in seen_ids:
            continue  # Skip invalid or previously seen agents
        similarity = fuzz.token_set_ratio(name.lower(), text_lower)
        if similarity >= fuzzy_threshold and name in agents_list:
            detected_names.append(name)
            detected_ids.append(agent_id)
            seen_ids.add(agent_id)

    return detected_names, detected_ids

# preprocess the content 
def preprocess_text(text_dict):
    # Ensure that 'text_dict' is a dictionary
    if isinstance(text_dict, dict):
        # Process each key-value pair and concatenate their values into a single string
        cleaned_text = " ".join(
            str(value).lower() for value in text_dict.values()
        )
        return cleaned_text
 
# takes documents and formats them into required format
def format_data(data, agents=None, ids=None):
    structured_data = []

    for file in data:
        category = file["category"]
        text = file["text"]

        if isinstance(text, list):  # If already parsed rows from Excel/CSV
            document_entries = text  # List of dicts
            search_text = " ".join(" ".join(str(v) for v in row.values()) for row in text)
        elif isinstance(text, dict):
            document_entries = [text]
            search_text = " ".join(str(v) for v in text.values())
        else:  # Assume raw string
            document_entries = [preprocess_text(text)]
            search_text = preprocess_text(text)

        detected_agents, detected_ids = detect_agents_ner(search_text, agents, ids)

        for agent_name, agent_id in zip(detected_agents, detected_ids):
            existing_agent = next((item for item in structured_data if (item["agent_id"] == agent_id and item["agent_name"] == agent_name)), None)

            if existing_agent:
                existing_agent["documents"].setdefault(category, []).extend(document_entries)
            else:
                structured_data.append({
                    "source": file["source"],
                    "agent_name": agent_name,
                    "agent_id": agent_id,
                    "documents": {
                        category: document_entries
                    }
                })
    print('here')
    return structured_data



directory = r"C:\Users\Evanw\OneDrive\Documents\GitHub\Summer2025\Prototype\data\Inputs"  
data = load_all_files(directory)

# Example agents and IDs
agents = ["Evan Wells","Haibin Zhu", "Jane Doe", "Alisa Stark","Allan Logan","Amy Jones","Andrew Grant","Angelica Peterson","Archie Dawson",
          "Aryanna Carney","Ashton Owen","Aubri Hartman","Aydin Pitts","Benjamin Roberts","Blake Booth","Braiden Santos",
          "Brantley Whitfield","Brayden Harding","Briley Mcknight","Bruno Johns","Bryan Murray","Callen Bentley","Chelsea Jimenez",
          "Conner Mcintyre","Daisy Pearce","Daniel Hill","David Kelly","Deon Griffith","Dominic Wood","Dylan Bailey","Dylan Baker",
          "Ella Green","Ella Powers","Ewan Pearson","Finlay Gardner","Finley Gray","Freya Price","George Jones","Georgia King",
          "Georgia Rogers","Heidi Wallace","Isabelle Gibson","Ivan Reese","Ivanna Boyer","Jack Walsh","Jaxson Giles","Jayden Rees",
          "Jessica Black","Johanna Duke","Jon Fischer","Joseph Burke","Kyle Shaw","Lacey Howard","Lauren Baker","Layne Terrell",
          "Libby Parker","Logan Ellis","Logan Mason","Matthew Reid","Max Miller","Michael Kaur","Milania Hodge","Niamh Walsh",
          "Noah Poole","Patrick Adams","Rachel Harper","Regan Rhodes","Rowan Cain","Rylan Mack","Scott Phillips","Seamus Noble",
          "Stephen Scott","Talon Miller","Valeria Crane","Xavier Mcdowell","Zachary Doyle","Zachary Turner","Zoe White", "Afreen Jamadar",
          "Alok Khandai", "Anvitha Rao", "arjun ks", "Arun Elumalai", "Ashalata Bisoyi", "Ashok Kunam", "Avin Sharma", "Ayesha B", "Ayushi Srivastava",
          "Bhawana Daf", "Darshan G.", "Dhanushkodi Raj", "Dinesh Reddy", "Dipesh Gulati", "Dushyant Bhatt", "Govardhana K", "Harini Komaravelli", 
          "Hartej Kathuria", "Ijas Nizamuddin", "Imgeeyaul Ansari", "Jay Madhavi", "Jitendra Babu", "Jyotirbindu Patnaik", "Karthihayini C", "Karthik GV", 
          "Kartik Sharma", "Kasturika Borah", "Kavitha K", "Kavya U.", "Khushboo Choudhary", "kimaya sonawane", "Koushik Katta", "Kowsick Somasundaram", "Lakshika Neelakshi", 
          "Madas Peddaiah", "Madhuri Sripathi", "Mahesh Vijay", "Manisha Bharti", "Manjari Singh", "Mohamed Ameen", "Mohini Gupta", "Navas Koya",
          "Navjyot Singh Rathore", "Nazish Alam", "Nidhi Pandit", "Nikhileshkumar Ikhar", "Nitin Tr", "Pradeeba V", "Prakriti Shaurya", "PRASHANTH BADALA", 
          "Pratibha P", "Prem Koshti", "Pulkit Saxena", "Puneet Singh", "Rahul Bollu", "Rajeev Kumar", "Ram Edupuganti", "Ramesh HP", "Ramya. P", "R Arunravi",
          "Ravi Shankar", "Ravi Shivgond", "Rohit Bijlani", "Roshan Sinha", "Sai Dhir", "Sai Patha", "Sai Vivek Venkatraman", "Sameer Kujur",
          "Samyuktha Shivakumar", "Santosh Ganta", "Sarfaraz Ahmad", "Senthil Kumar", "Shabnam Saba", "Shaheen Unissa", "Sharan Adla", "Shreyanshu Gupta",
          "Shrishti Chauhan", "Shubham Mittal", "Sivaganesh Selvakumar", "Snehal Jadhav", "Soumya Balan", "Soumya Balan", "Sowmya Karanth", "Srabani Das", 
          "Srinivas VO", "Srushti Bhadale", "Sudaya Puranik", "Sumit Kubade", "Syam Devendla", "Tejasri Gunnam", "Urshila Lohani", "Vamsi krishna", 
          "VARUN AHLUWALIA", "Vijayalakshmi Govindarajan", "Vikas Singh", "Yasothai Jayaramachandran", "Yathishwaran P", "Yogi Pesaru", "Anurag Asthana",
          "Syed Sadath ali", "Nida Khan", "Fenil Francis", "Gaurav Soni", "Viny Khandelwal", "amarjyot sodhi", "Sameer Kujur", "Zaheer Uddin", "Abdul B",
          "Bike Rally", "Girish Acharya", "Asha Subbaiah", "Divesh Singh", "Ramesh chokkala", "Ganesh AlalaSundaram", "Srinu Naik Ramavath", "Puneet Bhandari", 
          "Aarti Pimplay", "Bangalore Tavarekere", "Avani Priya", "Sanand Pal", "Partho Sarathi Mitra", "Pranay Sathu", "Tanmoy Maity", "Aanirudh Razdan", 
          "Shiksha Bhatnagar", "Chhaya Prabhale", "Karthik G V", "Mohammed Murtuza", "Saurabh Saurabh", "Prabhu Prasad Mohapatra", "Raja Chandra Mouli",
          "Krishna Prasad", "Dushyant Bhatt", "Soumya Balan", "pradeep chauhan", "Akansha Jain", "Rishabh soni", "Paul Rajiv", "Karan Turkar", "Akshay Dubey",
          "Sayani Goswami", "Sweety Garg", "Ramkrishan Bhatt", "B. Gokul", "Anand S", "Krishna Prasad", "Saurabh Sandhikar", "Priyesh Dubey", "Laya A", 
          "Vishwanath P", "Hemil Bhavsar", "Siddhartha Chetri", "Pratik Vaidya", "Ramakrishna Rao", "Keshav Dhawale", "Praveen Bhaskar", "Gunjan Nayyar",
          "Rupesh Reddy", "Puneeth R", "Kandrapu Reddy", "Vineeth Vijayan", "Rahul Tayade", "Debasish Dasgupta", "Suresh Kanagala", "Jaspreet Kaur", 
          "Somanath Behera", "Ashish Indoriya", "Dilliraja Baskaran", "Deepika S", "Jacob Philip", "Yogesh Ghatole", "Ajay Elango", "Shaik Tazuddin", 
          "Angad Waghmare", "Sohan Dhakad", "Madhava Konjeti", "Shreya Agnihotri", "Tapan kumar Nayak", "Arpit Jain", "Palani S", "Meenalochani Kondya", 
          "Shrinidhi Selva Kumar", "Mayank Shukla", "Shraddha Achar", "Arpit Godha", "Jatin Arora", "Karthik Gururaj", "Akila Mohideen", "Ahmad Bardolia",
          "Puran Mal", "Sridevi H", "Raktim Podder", "Pavithra M", "shrikant desai", "Kiran Kumar", "Chaban kumar Debbarma", "Akash Gulhane", "K. Siddharth",
          "Shivam Rathi", "Nitin Verma", "Venkateswara D", "Shivasai Mantri", "Prasanna Ignatius", "Pankaj Bhosale", "Vinay Singhal", "Pawan Nag", 
          "Shivam Sharma", "Gaikwad Dilip", "Moumita Mitra", "Suman Biswas", "Mansi Thanki", "Anil Kumar", "Siddharth Choudhary", "Valarmathi Dhandapani", 
          "Pradeep Kumar", "Hemal Patel", "Bipul Poddar", "Bipul Poddar", "Rahul Pal", "Ajay Gupta", "sneh jain", "Rahul singh", "Hemal Patel", "Shharad Sharma",
          "sneh jain", "Ram Dubey", "MUKESH SHAH", "Ram Dubey", "Murtuza Rawat", "Rajesh Rokaya", "Akshay Gandhi", "Aakash Dodia", "Wilfred Anthony", 
          "Jaykumar Shah", "Suresh Singh", "Sayed Shamim Azima", "Atul Dwivedi", "Vikas Suryawanshi", "Nitesh Raheja", "RIYAZ SHAIKH", "Alok Gond", 
          "Shodhan Pawar", "Zeeshan Mirza", "Mohammad Khan", "Satyendra Singh", "Manojkumar Bora", "Sanjeev Shahi", "Tahir Pasa", "Sweety Kakkar", 
          "Priyanka Sonar", "Sajauddin Khan", "Sameer Toraskar", "Tapan Kathekar", "Manas Chhualsingh", "Riya Jacob", "Jaison Tom", "Amol Bansode", 
          "Binoy Choubey", "Atul Ranade", "Ajit Kumar", "Deepak Pant", "Parvez Modi", "Shalet Fernandes", "Aman Panfeyy", "Ritesh Tiwari", "Satyendra Singh", 
          "aaryan vatts", "Ritesh Tiwari", "Sanjivv Dawalle", "Rajani G", "Pranav Samant", "Aniket Bagul", "Satish Patil", "Shridhar Shegunshi", "Samar Vakharia", 
          "Anish Sant Kumar Gupta", "Aman Panfeyy", "Kishor Patil", "Sweta Makwana", "Manoj Chawla", "Saad alam Siddiqui", "Ravi Prakash Srivastava", 
          "Harpreet Kaur Lohiya", "Reshma Raeen", "Mahesh. Shrigiri", "Shujatali Kazi", "Rajesh Rokaya", "Shaikh Nasreen", "Kanhai Jee", "Ravindra Verma", 
          "Sambhaji Shivankar", "Swapna Sanadi", "Nilesh Sinha", "Vikram Rajput", "Mohammad Khan", "Pranav Samant", "AMIT DUBEY", "Nipul Goyal", "Rajesh Davankar", 
          "Phiroz Hoble", "Shrikant V", "Harpreet Kaur Lohiya", "Liston Souza", "MUKESH SHAH", "Sandeep Dube", "Harinath Rudra", "Shailesh Jadhav", "Mayur Talele", 
          "Naveed Chaus", "Mukesh Gind", "Punit Raghav", "Punit Raghav", "Bhupesh Singh", "Saqib Syed", "Sandeep Dube", "Vipin Jakhaliya", "Romy Dhillon", 
          "Vinayak Sambharap", "Pratham Shetty", "Pradyuman Nayyar", "Sameer More", "Sanket Rastogi", "Prashant Chitare", "Amrata Rajani", "Pawan Yadav", 
          "Noor Khan", "Ravi Shahade", "Neha Lakhanpal", "Rohit Chachad", "Chandansingh Janotra", "Caesar Silveira", "Kuntal Dandir", "Irfan Ansari", "Vijay Shinde", 
          "Himanshu Ganvir", "Prembahadur Kamal", "Kartik Mehta", "Sweta Makwana", "Shreyas Chippalkatti", "Naynish Argade", "Rahul Karkera", "Vinita Berde", 
          "Sweta Makwana", "Sameer More", "Laveline Soans", "New folder (4)/Ajit-Kumar (1).pdf", "Prasad Dalvi", "Mahesh Chalwadi", "Hardik Shah", 
          "Brijesh Shetty", "Amith Panicker", "Ajit Kumar", "New folder (4)/Ajit-Kumar (1).pdf", "Ansh Kachhara", "Shehzad Hamidani", "Raunak dambir Dambir", 
          "manoj singh", "Lokesh Inarkar", "Shaikh Ansar", "Navneet Trivedi", "Dattatray Shinde", "Harshall Gandhi", "John Arthinkal", "Lokmanya Pada", 
          "Mohammed Khan", "Neeraj Dwivedi", "Sana Anwar Turki", "Sheldon Creado", "Jameel Pathan", "Prashant Pattekar", "Sougata Goswami", "Vaibhav Pawar", 
          "Sneha Rajguru", "Niyaz Ahmed Chougle", "Rakesh Tikoo", "Ansh Kachhara", "Tarun Chhag", "Nikkhil Chitnis", "AARTI MHATRE", "Mahesh. Shrigiri", 
          "Ksheeroo Iyengar", "Rohan Deshmukh", "Avantika Rathore", "Yash Raja", "SUFIYAN Motiwala", "Abhishek Jha", "Afreen Jamadar", "Akhil Yadav Polemaina", 
          "Alok Khandai", "Ananya Chavan", "Anvitha Rao", "arjun ks", "Arun Elumalai", "Ashalata Bisoyi", "Ashok Kunam", "Asish Ratha", "Avin Sharma", "Ayesha B", 
          "Ayushi Srivastava", "Bhawana Daf", "Darshan G.", "Dhanushkodi Raj", "Dinesh Reddy", "Dipesh Gulati", "Dushyant Bhatt", "Govardhana K", "Harini Komaravelli", 
          "Hartej Kathuria", "Ijas Nizamuddin", "Imgeeyaul Ansari", "Jay Madhavi", "Jitendra Babu", "Jyotirbindu Patnaik", "Karthihayini C", "Karthik GV", 
          "Kartik Sharma", "Kasturika Borah", "Kavitha K", "Kavya U.", "Khushboo Choudhary", "kimaya sonawane", "Koushik Katta", "Kowsick Somasundaram", 
          "Lakshika Neelakshi", "Madas Peddaiah", "Madhuri Sripathi", "Mahesh Vijay", "Manisha Bharti", "Manjari Singh", "Mohamed Ameen", "Mohini Gupta", 
          "Navas Koya", "Navjyot Singh Rathore", "Nazish Alam", "Nidhi Pandit", "Nikhileshkumar Ikhar", "Nitin Tr", "Pradeeba V", "Prakriti Shaurya", 
          "PRASHANTH BADALA", "Puneet Singh", "Rahul Bollu", "Rajeev Kumar", "Ram Edupuganti", "Ramesh HP", "Ramya. P", "R Arunravi", "Ravi Shankar", 
          "Ravi Shivgond", "Rohit Bijlani", "Roshan Sinha", "Sai Dhir", "Sai Patha", "Sai Vivek Venkatraman", "Sameer Kujur", "Samyuktha Shivakumar", 
          "Santosh Ganta", "Sarfaraz Ahmad", "Shabnam Saba", "Shaheen Unissa", "Sharan Adla", "Shreyanshu Gupta", "Sivaganesh Selvakumar", "Snehal Jadhav", 
          "Soumya Balan", "Soumya Balan", "Sowmya Karanth", "Sumit Kubade", "Vijayalakshmi Govindarajan", "Sameer Kujur", "Zaheer Uddin", "Abdul B", "Bike Rally", 
          "Divyesh Mishra", "Shreekumar Das", "Bharat Sharma", "Karthikeyan Mani", "Abbas Reshamwala", "Pradeep R shukla Shukla", "Laxmiprasad Ukidawe", 
          "Masurkar Vijay", "Vaibhav Ghag", "Siddhanth Jaisinghani", "Adil K", "Mayuresh Patil", "Sandip Gajre", "Naveed Chaus", "Ankit Shah", "Ashwini Vartak", 
          "Manisha Surve", "Yash Patil", "Adil K", "Ajith Gopalakrishnan", "AARTI MHATRE", "Abbas Reshamwala", "Gajendra Dhatrak", "H.N Arun Kumar", 
          "Naynish Argade", "Mohammad Khalil", "Prashant Pawar", "Sagar Kurada", "Sandeep Mahadik", "Sumedh Tapase", "Vijay Mahadik", "Ammit Sharma", 
          "Deepak Manjrekar", "Deepak Manjrekar", "Dinesh Pawa", "Jitendra. Makhijani", "Raisuddin Khan", "Sameer Gavad", "Sapeksha Satam", "Sunil Palande", 
          "Tejbal Singh", "Ashish Dubey", "Bhaskar Gupta", "Bhupesh Singh", "Bikram Bhattacharjee", "Chinmoy Choubey", "Jitendra Razdan", "Mukesh Gind", 
          "Nadeem Sayyed", "Prashant Narayankar", "Rohinton Vasania", "Anuj Mishra", "Bhat Madhukar", "Hitesh Sabnis", "Kelvin Fernandes", "Mohshin Khan", 
          "Prashant Jagtap", "Rafique Kazi", "Saad alam Siddiqui", "Shaileshkumar Mishra", "Sushant Vatare", "Amarjeet Bhambra", "Atif Khan", "Jalil Bhanwadia", 
          "Krishna Saha", "Kuntal Dandir", "Madhurendra Kumar Singh", "Mahesh Gokral", "Rajnish Dubey", "Subramaniam Sabarigiri", "Tarun Chhag", "Vijay Kothe", 
          "Vikram Hirugade", "Neelam Ohari", "Neelam Ohari", "Reema Asrani", "Sastha Nair", "Vincent Paul", "Aboli Patil", "Gohil kinjal", 
          "k.balaji krishnamoorthy", "Kalyani Parihar", "Mohd. Chaman", "Vishal Ankam", "D.ALDRIN DAVID", "Hemant Tupe", "Pritesh Gandhi", "Rohit Solanki", 
          "Shiv Singh", "Abbas Parve", "Abhijeet Srivastava", "Apoorva Singh", "Ashok Singh", "Gautam Palit", "Jitendra Sampat", "Kshitij Jagtap", 
          "Pankti Patel", "Tejas Achrekar", "Vinod Mohite", "Vivek Mishra", "Jyotirbindu Patnaik", "Karthihayini C", "Madhuri Sripathi", "VARUN AHLUWALIA", 
          "Aarti Pimplay", "Karthik Gururaj", "Raktim Podder", "Pavithra M", "shrikant desai", "Tahir Pasa", "Punit Raghav", "Tarun Chhag", "Puneet Singh", 
          "Sarfaraz Ahmad", "Chinmoy Choubey", "Abdul Faim khan", "Aditi Solanki", "Anirban Ghosh", "Anshika S", "Arunbalaji. R", "Ishan Bainsala", 
          "Kundan Kumar", "Lucky Singh", "Mansi Sharma", "Sharadhi TP", "Shreya Biswas", "Nitin Tr", "Sanand Pal", "Siddhartha Chetri", "Suresh Kanagala",
           "Mayank Shukla", "shrikant desai", "Jaison Tom", "Hartej Kathuria", "Adil K", "Sushant Vatare", "Sastha Nair", "Pankti Patel", "Suman Biswas",
           "aaryan vatts", "Shaheen Unissa", "Kuntal Dandir", "Sastha Nair", "Anil Jinsi", "Gaurav Swami", "Neelam Poonia", "Pawan Shukla", "Suchita Singh", 
           "Vinod Yadav", "Vipan Kumar", "Ajit Kumar", "Jitendra Razdan", "Kuntal Dandir", "Anil Jinsi", "Abuzar Shamsi", "Lucky Aneja", "Manoj Verma", 
           "rajeev nigam", "Riyaz Siddiqui", "Shivam Mishra", "Ugranath Kumar", "manoj singh", "Kshitij Jagtap", "Abheek Chatterjee", "Ashu Sandhu", 
           "B. Varadarajan", "Jignesh Trivedi", "Lalish P", "Rahi Jadhav", "Tarak.H. Joshi", "Vijay Kshirsagar", "Ashish Khanna", "Chandan Mandal", 
           "Chandrashekhar javalkote", "Dileep Nair", "Niranjan Tambade", "Sandeep Anand", "Vanmali Kalsara", "Mohini Gupta", "Adil K", "Ashok Dixit", 
           "Irfan Dastagir", "Kalpesh Shah", "Pritam Oswal", "Rajibaxar Nadaf", "Rohit Kumar", "Vikas Soni", "Yuvaraj Balakrishnan", "Zeeshan Mirza", 
           "Kiran Kumar", "Ankita Bedre", "Ashok Dixit", "ASHWINI DASARI", "Deepti Bansal", "Parveen Khatri", "Pawar susheelkumar", "Prathap Kontham", 
           "Rahul Kumar", "Rajat Singh", "Sachin Kumar", "Abhishek Tripathi", "Ashith Sivanandan", "Mithun Rathod", "Prosenjit Mitra", "Rahul Kumar", 
           "Shibin Raveendran", "Susant Parida", "Udayakumar Sampath", "K Murty", "Irfan Shaikh", "Jayesh Joshi", "Prashant Duble", 
           "Rayees Parwez", "Sachin Kushwah", "Sakshi Sundriyal", "Vijat Kumar"]

ids = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, None, None, None, None, "00001", "00002", "00003", "00004", "00005", 
        "00006", "00007", "00008", "00009", "00010", "00011", "00012", "00013", "00014", "00015", "00016", "00017", 
        "00018", "00019", "00020", "00021", "00022", "00023", "00024", "00025", "00026", "00027", "00028", "00029", 
        "00030", "00031", "00032", "00033", "00034", "00035", "00036", "00037", "00038", "00039", "00040", "00041", 
        "00042", "00043", "00044", "00045", "00046", "00047", "00048", "00049", "00050", "00051", "00052", "00053", 
        "00054", "00055", "00056", "00057", "00058", "00059", "00060", "00061", "00062", "00063", "00064", "00065", 
        "00066", "00067", "00068", "00069", "00070", "00071", "00072", "00073", "00074", "00075", "00076", "00077", 
        "00078", "00079", "00080", "00081", "00082", "00083", "00084", "00085", "00086", "00087", "00088", "00089", 
        "00090", "00091", "00092", "00093", "00094", "00095", "00096", "00097", "00098", "00099", "00100", "00101", 
        "00102", "00103", "00104", "00105", "00106", "00107", "00108", "00109", "00110", "00111", "00112", "00113", 
        "00114", "00115", "00116", "00117", "00118", "00119", "00120", "00121", "00122", "00123", "00124", "00125", 
        "00126", "00127", "00128", "00129", "00130", "00131", "00132", "00133", "00134", "00135", "00136", "00137", 
        "00138", "00139", "00140", "00141", "00142", "00143", "00144", "00145", "00146", "00147", "00148", "00149", 
        "00150", "00151", "00152", "00153", "00154", "00155", "00156", "00157", "00158", "00159", "00160", "00161", 
        "00162", "00163", "00164", "00165", "00166", "00167", "00168", "00169", "00170", "00171", "00172", "00173", 
        "00174", "00175", "00176", "00177", "00178", "00179", "00180", "00181", "00182", "00183", "00184", "00185", 
        "00186", "00187", "00188", "00189", "00190", "00191", "00192", "00193", "00194", "00195", "00196", "00197", 
        "00198", "00199", "00200", "00201", "00202", "00203", "00204", "00205", "00206", "00207", "00208", "00209", 
        "00210", "00211", "00212", "00213", "00214", "00215", "00216", "00217", "00218", "00219", "00220", "00221", 
        "00222", "00223", "00224", "00225", "00226", "00227", "00228", "00229", "00230", "00231", "00232", "00233", 
        "00234", "00235", "00236", "00237", "00238", "00239", "00240", "00241", "00242", "00243", "00244", "00245", 
        "00246", "00247", "00248", "00249", "00250", "00251", "00252", "00253", "00254", "00255", "00256", "00257", 
        "00258", "00259", "00260", "00261", "00262", "00263", "00264", "00265", "00266", "00267", "00268", "00269", 
        "00270", "00271", "00272", "00273", "00274", "00275", "00276", "00277", "00278", "00279", "00280", "00281", 
        "00282", "00283", "00284", "00285", "00286", "00287", "00288", "00289", "00290", "00291", "00292", "00293", 
        "00294", "00295", "00296", "00297", "00298", "00299", "00300", "00301", "00302", "00303", "00304", "00305", 
        "00306", "00307", "00308", "00309", "00310", "00311", "00312", "00313", "00314", "00315", "00316", "00317", 
        "00318", "00319", "00320", "00321", "00322", "00323", "00324", "00325", "00326", "00327", "00328", "00329", 
        "00330", "00331", "00332", "00333", "00334", "00335", "00336", "00337", "00338", "00339", "00340", "00341", 
        "00342", "00343", "00344", "00345", "00346", "00347", "00348", "00349", "00350", "00351", "00352", "00353", 
        "00354", "00355", "00356", "00357", "00358", "00359", "00360", "00361", "00362", "00363", "00364", "00365", 
        "00366", "00367", "00368", "00369", "00370", "00371", "00372", "00373", "00374", "00375", "00376", "00377", 
        "00378", "00379", "00380", "00381", "00382", "00383", "00384", "00385", "00386", "00387", "00388", "00389", 
        "00390", "00391", "00392", "00393", "00394", "00395", "00396", "00397", "00398", "00399", "00400", "00401", 
        "00402", "00403", "00404", "00405", "00406", "00407", "00408", "00409", "00410", "00411", "00412", "00413", 
        "00414", "00415", "00416", "00417", "00418", "00419", "00420", "00421", "00422", "00423", "00424", "00425", 
        "00426", "00427", "00428", "00429", "00430", "00431", "00432", "00433", "00434", "00435", "00436", "00437", 
        "00438", "00439", "00440", "00441", "00442", "00443", "00444", "00445", "00446", "00447", "00448", "00449", 
        "00450", "00451", "00452", "00453", "00454", "00455", "00456", "00457", "00458", "00459", "00460", "00461", 
        "00462", "00463", "00464", "00465", "00466", "00467", "00468", "00469", "00470", "00471", "00472", "00473", 
        "00474", "00475", "00476", "00477", "00478", "00479", "00480", "00481", "00482", "00483", "00484", "00485", 
        "00486", "00487", "00488", "00489", "00490", "00491", "00492", "00493", "00494", "00495", "00496", "00497", 
        "00498", "00499", "00500", "00501", "00502", "00503", "00504", "00505", "00506", "00507", "00508", "00509", 
        "00510", "00511", "00512", "00513", "00514", "00515", "00516", "00517", "00518", "00519", "00520", "00521", 
        "00522", "00523", "00524", "00525", "00526", "00527", "00528", "00529", "00530", "00531", "00532", "00533", 
        "00534", "00535", "00536", "00537", "00538", "00539", "00540", "00541", "00542", "00543", "00544", "00545", 
        "00546", "00547", "00548", "00549", "00550", "00551", "00552", "00553", "00554", "00555", "00556", "00557", 
        "00558", "00559", "00560", "00561", "00562", "00563", "00564", "00565", "00566", "00567", "00568", "00569", 
        "00570", "00571", "00572", "00573", "00574", "00575", "00576", "00577", "00578", "00579", "00580", "00581", 
        "00582", "00583", "00584", "00585", "00586", "00587", "00588", "00589", "00590", "00591", "00592", "00593", 
        "00594", "00595", "00596", "00597", "00598", "00599", "00600", "00601", "00602", "00603", "00604", "00605", 
        "00606", "00607", "00608", "00609", "00610", "00611", "00612", "00613", "00614", "00615", "00616", "00617", 
        "00618", "00619", "00620", "00621", "00622", "00623", "00624", "00625", "00626", "00627", "00628", "00629", 
        "00630", "00631", "00632", "00633", "00634", "00635", "00636", "00637", "00638", "00639", "00640", "00641", 
        "00642", "00643", "00644", "00645", "00646", "00647", "00648", "00649", "00650", "00651", "00652", "00653", 
        "00654", "00655", "00656", "00657", "00658", "00659", "00660", "00661", "00662", "00663", "00664", "00665", 
        "00666", "00667", "00668", "00669", "00670", "00671", "00672", "00673", "00674", "00675", "00676", "00677", 
        "00678", "00679", "00680", "00681", "00682", "00683", "00684", "00685", "00686", "00687", "00688", "00689", 
        "00690", "00691", "00692", "00693", "00694", "00695", "00696", "00697", "00698", "00699", "00700", "00701"]

preprocessed_data = format_data(data, agents, ids)


