import { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { Trash } from 'lucide-react';
import '../styles/agent.css';

const AgentsPage = ({userId}) => {
  const [agents, setAgents] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newAgent, setNewAgent] = useState({ firstName: "", lastName: "", id: "" });
  const [loading, setLoading] = useState(false);

  // loads agents upon load
  useEffect(() => {
    axios.get(`/api/agents/${userId}`)
      .then(response => {
        setAgents(Array.isArray(response.data) ? response.data : []);
      })
      .catch(err => {
        console.error("Error fetching agents", err);
        setAgents([]);
      });
  }, [userId]);

  useEffect(() => {
    console.log("Loaded agents:", agents);
  }, [agents]);

// to display option to add agent
 const handleAddAgentClick = () => {
    setShowAddForm(true);
  };

  // handles adding new attribute to new agent
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewAgent((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // handles deleteing agent form db
  const handleDeleteAgent = async (agent_num) => {
    if (!window.confirm("Are you sure you want to delete this agent?")) return;

    try {
      await axios.delete(`/api/agents/${agent_num}`);
      window.location.reload(); // reloads page to show changes
    } catch (error) {
      console.error("Failed to remove agent", error);
    }
  };

  // takes new agent info and adds to db
  const handleAddAgentSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); //loading indication
    
    try { // send new agent entity to post req
      console.log("Submitting agent:", newAgent);
      const response = await axios.post(`/api/agents/${userId}`, {
        AGENT_ID: newAgent.id ? Number(newAgent.id) : null,
        FIRST_NAME: newAgent.firstName,
        LAST_NAME: newAgent.lastName,
      });
      
      setAgents(prev => [...prev, response.data]);
      setNewAgent({ firstName: "", lastName: "", id: ""});
      setShowAddForm(false);
    } 
    catch (error) { // display errors to console
      console.error("Failed to add agent", error);
    } 
    finally { //for users to see
      setLoading(false);
    }
  };


  return (
    <div className="agents-container">
      <h2>Agents</h2>
      <div>
          <p className="text">
            No agents are currently added for evaluation. Press Add New Agents to add. Add an agent ID if applicable. Agents must be added to be identified within documents. 
          </p>
        </div>
      {Array.isArray(agents) && agents.length > 0 ? (
        agents.map((agent, index) => (
          <div key={index} className="agent-card">
            <div className="agent-info">
              <p className="agent-name">
                {agent.FIRST_NAME || agent.firstName} {agent.LAST_NAME || agent.lastName}
              </p>
              <p className="agent-id">ID: {agent.AGENT_ID || agent.iD}</p>
            </div>
            <button
              onClick={() => handleDeleteAgent(agent.AGENT_NUM)}
              className="delete-button"
              title="Remove agent"
            >
              <Trash size={20} className="trash-icon" />
            </button>
          </div>
        ))
      ) : (
        <div>
          <h2 className="text">
           No Agents added.
          </h2>
        </div>
      )}


      {/* Inline Add New Agent Form */}
      {showAddForm ? (
        <form onSubmit={handleAddAgentSubmit} className="add-agent-form" style={{ marginTop: "1rem" }}>
          <input
            type="text"
            name="firstName"
            placeholder="First Name"
            value={newAgent.firstName}
            onChange={handleInputChange}
            required
          />
          <input
            type="text"
            name="lastName"
            placeholder="Last Name"
            value={newAgent.lastName}
            onChange={handleInputChange}
            required
          />
          <input
            type="number"
            name="id"
            placeholder="ID"
            value={newAgent.id}
            onChange={handleInputChange}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Adding..." : "Add Agent"}
          </button>
          <button type="button" onClick={() => setShowAddForm(false)} disabled={loading} style={{ marginLeft: '0.5rem' }}>
            Cancel
          </button>
        </form>
      ) : (
        <button className="add-agent-button" onClick={handleAddAgentClick} style={{ marginTop: "1rem" }}>
          Add New Agent
        </button>
      )}
        <div className="spacer" />
        <Link to="/roles" className="button-container">
          <button className="proceed-button"> Proceed to Role Definition </button>
        </Link>
    </div>
  );
};

export default AgentsPage;