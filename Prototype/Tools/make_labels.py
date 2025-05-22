import random

agents = ["Evan Wells","Haibin Zhu", "Jane Doe", "Alisa Stark","Allan Logan","Amy Jones","Andrew Grant","Angelica Peterson","Archie Dawson",
          "Aryanna Carney","Ashton Owen","Aubri Hartman","Aydin Pitts","Benjamin Roberts","Blake Booth","Braiden Santos",
          "Brantley Whitfield","Brayden Harding","Briley Mcknight","Bruno Johns","Bryan Murray","Callen Bentley","Chelsea Jimenez",
          "Conner Mcintyre","Daisy Pearce","Daniel Hill","David Kelly","Deon Griffith","Dominic Wood","Dylan Bailey","Dylan Baker",
          "Ella Green","Ella Powers","Ewan Pearson","Finlay Gardner","Finley Gray","Freya Price","George Jones","Georgia King",
          "Georgia Rogers","Heidi Wallace","Isabelle Gibson","Ivan Reese","Ivanna Boyer","Jack Walsh","Jaxson Giles","Jayden Rees",
          "Jessica Black","Johanna Duke","Jon Fischer","Joseph Burke","Kyle Shaw","Lacey Howard","Lauren Baker","Layne Terrell",
          "Libby Parker","Logan Ellis","Logan Mason","Matthew Reid","Max Miller","Michael Kaur","Milania Hodge","Niamh Walsh",
          "Noah Poole","Patrick Adams","Rachel Harper","Regan Rhodes","Rowan Cain","Rylan Mack","Scott Phillips","Seamus Noble",
          "Stephen Scott","Talon Miller","Valeria Crane","Xavier Mcdowell","Zachary Doyle","Zachary Turner","Zoe White"]

#list of roles here plz
roles = [
    "Leadership", "Cooperation", "Adaptability", "Creativity", "Problem Solving", "Communication", "Teamwork", 
    "Flexibility", "Decision Making", "Innovation", "Time Management", "Conflict Resolution", "Motivation",
    "Strategic Thinking", "Responsibility", "Customer Focus"
]

# Open and create .txt file for writing
with open("agents_roles.txt", "w") as file:
    for agent in agents:
        # Pick 4 random roles
        random_roles = random.sample(roles, 4)
        
        # Generate random values for the role scores between 0 and 1
        role_scores = {role: round(random.uniform(0.5, 1), 2) for role in random_roles}
        
        # Format each agent's role string with indentation
        file.write(f'"{agent}": {{\n')
        
        for role, score in role_scores.items():
            file.write(f'    "{role}": {score},\n')
        
        # Remove the last comma and newline, then close the JSON object
        file.seek(file.tell() - 2, 0)  # Move the cursor back to overwrite the last comma
        file.write('\n},\n')

print("Data has been written to 'agents_roles.txt'.")