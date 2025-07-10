import { useEffect, useState, useMemo  } from "react";
import axios from "axios";
import "../../styles/evaluation.css";
import { useNavigate, useParams } from "react-router-dom";

const AgentConstraintsSetup = () => {
  const { userId } = useParams();
  const [agents, setAgents] = useState([]);
  const [roles, setRoles] = useState([]);
  const [amount, setAmount] = useState([]);
  const [loading, setLoading] = useState(true);
  const [applyAllValue, setApplyAllValue] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await axios.get(`/api/assignments/GMRA_2/${userId}`);
        setAgents(
          (res.data.agents || []).map((agent) => ({
            ...agent,
            max_roles: 0, // default value
          }))
        );
        setRoles(res.data.roles || []);
        setAmount(res.data.amount || 0)
      } catch (error) {
        console.error("Failed to load agent data", error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [userId]);

  const handleRoleLimitChange = (index, value) => {
    const max = roles.length;
    const parsed = Math.max(0, Math.min(parseInt(value) || 0, max));
    const updated = [...agents];
    updated[index].max_roles = parsed;
    setAgents(updated);
  };

  const handleApplyAll = () => {
    const max = roles.length;
    const val = Math.max(0, Math.min(parseInt(applyAllValue) || 0, max));
    const confirmApply = window.confirm(
      `Are you sure you want to set max roles = ${val} for all ${agents.length} agents?`
    );
    if (confirmApply) {
      const updated = agents.map(agent => ({
        ...agent,
        max_roles: val
      }));
      setAgents(updated);
      setApplyAllValue(val.toString()); // update field to clamped value
    }
  };

  const handleSubmit = async () => {
    const totalAssigned = agents.reduce((sum, agent) => sum + (agent.max_roles || 0), 0);

    if (totalAssigned < amount) {
      alert(`Total assigned roles (${totalAssigned}) must be at least ${amount}.`);
      return;
    }

    try {
      const payload = agents.map((agent) => ({
        AGENT_NUM: agent.AGENT_NUM,
        MAX_ROLES: agent.max_roles,
      }));

      await axios.post(`/api/assignments/GMRA_2/agents/${userId}`, payload);
      navigate(`/assignment/GMRA3/${userId}`);
    } catch (error) {
      console.error("Submission error", error);
      alert("Error submitting agent constraints");
    }
  };
   if (agents.length <= 1) {
    return (
      <div>
        <h2>Agent Constraints</h2>
        <p className="text"> Here, you may decide how many roles each agent may take on. The Apply All button applies the input number to all agents. You can press Skip This Step if 
          you would like to use the previous setup.
        </p>
        <h2 className="text">
          No agents or not enough agents found. Please add agents to proceed with the assignment.
        </h2>
      </div>
    );
  }
  return (
    <div>
      <h2>Agent Constraints</h2>
      <p className="text">
          Here, you may decide how many roles each agent may take on. The Apply All button applies the input number to all agents. You can press Skip This Step if 
          you would like to use the previous setup.
        </p>
      <div className="evaluation-container">
        <div className="evaluation-inner">
          <div className="apply-all-wrapper">
            <input
              type="number"
              min="0"
              placeholder="0"
              value={applyAllValue}
              onChange={(e) => setApplyAllValue(e.target.value)}
              className="editable-cell"
              style={{ width: "4rem" }}
            />
            <button
              className="apply-all-button"
              onClick={handleApplyAll}
              disabled={!applyAllValue}
            >
              Apply to All
            </button>
          </div>
          </div>
          <p style={{ marginBottom: "1rem", fontWeight: "bold" }}>
            Maximum playable roles per agent: {roles.length}
          </p>

          <table className="evaluation-table">
            <thead>
              <tr>
                <th>Agent</th>
                <th>Max Roles</th>
              </tr>
            </thead>
            <tbody>
              {agents.map((agent, idx) => (
                <tr key={agent.AGENT_NUM}>
                  <td>{agent.FIRST_NAME} {agent.LAST_NAME}</td>
                  <td>
                    <input
                      type="number"
                      min="0"
                      max={roles.length}
                      value={agent.max_roles}
                      onChange={(e) => handleRoleLimitChange(idx, e.target.value)}
                      className="editable-cell"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="upload-button" onClick={handleSubmit} disabled={loading}>
              Save Constraints
            </button>
            <button
              className="upload-button"
              style={{ backgroundColor: "#ccc" }}
              onClick={() => navigate(`/assignment/GMRA3/${userId}`)}
            >
              Skip This Step
            </button>
          </div>
        </div>
      </div>
    
  );
};

export default AgentConstraintsSetup;
