import { useEffect, useState } from "react";
import axios from "axios";
import '../../styles/evaluation.css';
import { useNavigate } from "react-router-dom";

const GRA = ({ userId }) => {
  const [roles, setRoles] = useState([]);
  const [user, setUser] = useState({});
  const [totalRoles, setTotalRoles] = useState(0);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await axios.get(`/api/assignments/GRA_1/${userId}`);
        setRoles(response.data.roles || []);
        setUser(response.data.user || {});
        setTotalRoles(response.data.agents?.length || 0);
      } catch (error) {
        console.error("Failed to load GRA data", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [userId]);

  const totalAssigned = roles.reduce((sum, role) => sum + (parseInt(role.required_agents) || 0), 0);

  const handleRoleCountChange = (index, value) => {
    const parsedValue = Math.max(0, parseInt(value) || 0);
    const newTotal = totalAssigned - (parseInt(roles[index].required_agents) || 0) + parsedValue;

    if (newTotal > totalRoles) {
      alert(`You only have ${totalRoles} agents. Total assigned cannot exceed this.`);
      return;
    }

    const updatedRoles = [...roles];
    updatedRoles[index].required_agents = parsedValue;
    setRoles(updatedRoles);
  };

  const handleSubmit = async () => {
    try {
      const payload = roles.map(r => ({
        DEFINING_WORD: r.defining_word,
        REQUIRED_AGENTS: r.required_agents
      }));
      await axios.post(`/api/assignments/GRA/roles/${userId}`, payload);
      navigate(`/assignment/GRA2/${userId}`);
    } catch (error) {
      console.error("Submission error", error);
      alert("Error submitting assignment");
    }
  };
  
  if (roles.length <= 1) {
    return (
      <div>
        <h2>GMRA Assignment Setup</h2>
        <p className="text"> Here, you may decide how many agents will need to be playing each role for the specified task. You may press Skip This Step if 
        you would like to use the previous setup. 
        </p>
        <h2 className="text">
          No roles or not enough roles found. Please add roles to proceed with the assignment.
        </h2>
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>GRA Assignment Setup</h2>
      </div>
      <p className="text">
          Here, you may decide how many agents will need to be playing each role for the specified task. You may press Skip This Step if 
          you would like to use the previous setup.
        </p>
      <div  className="evaluation-container">
        
        <table className="evaluation-table">
          <thead>
            <tr>
              <th>Role</th>
              <th>Required Agents</th>
            </tr>
          </thead>
          <tbody>
            {roles.map((role, idx) => (
              <tr key={role.role}>
                <td>{role.role}</td>
                <td>
                  <input
                    type="number"
                    min="0"
                    value={role.required_agents}
                    onChange={(e) => handleRoleCountChange(idx, e.target.value)}
                    className="editable-cell"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="upload-button" onClick={handleSubmit} disabled={loading}>
            Save Assignment
          </button>
          <button
            className="upload-button"
            style={{ backgroundColor: '#ccc'}}
            onClick={() => navigate(`/assignment/GRA2/${userId}`)}
          >
            Skip This Step
          </button>
        </div>
      </div>
      </div>
   
  );
};

export default GRA;