import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import axios from "axios";
import '../../styles/evaluation.css';

const GMRAMatrixPage = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [hasConflict, setHasConflict] = useState(false);
  const [hasCooperation, setHasCooperation] = useState(false);
  const [roles, setRoles] = useState([]);
  const [agents, setAgents] = useState([]);
  const [evaluations, setEvaluations] = useState({});
  const [matrix, setMatrix] = useState([]);
  const [user, setUser] = useState({});
  const [loading, setLoading] = useState(true);
  const [useConflicts, setUseConflicts] = useState(false);
  const [conflictMatrixExists, setConflictMatrixExists] = useState(true);
  const [conflictError, setConflictError] = useState("");

  useEffect(() => {
    if (!userId) return;

    async function fetchMatrix() {
      try {
        const res = await axios.get(`/api/assignments/GMRA/matrix/${userId}`);
        setRoles(res.data.roles || []);
        setAgents(res.data.agents || []);
        setEvaluations(res.data.evaluations || {});
        setMatrix(res.data.matrix || []);
        setUser(res.data.user || {});
      } catch (err) {
        console.error("Failed to load matrix data", err.response?.data || err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchMatrix();
  }, [userId]);

  const handleConsiderMatrix = async (cooperation) => {
    try {
      const res = await axios.post(
        `/api/assignments/GMRA/consider_constraints/${userId}`,
        { cooperation }
      );

      if (res.data.matrix) {
        setMatrix(res.data.matrix);
        setUseConflicts(true);
        alert(
          cooperation
            ? "Optimal results considering cooperation received."
            : "Optimal results considering conflicts received."
        );
      } else {
        alert("Too many constraints to produce results. Consider reducing role count or conflicts.");
      }
    } catch (err) {
      console.error("Failed to apply constraint-aware assignment", err);
      alert("Could not apply constraint-aware assignment.");
    }
  };

    useEffect(() => {
    if (!userId) return;

    async function checkConflictMatrix() {
      try {
        const res = await axios.get(`/api/assignments/conflicts/${userId}`);
        setHasConflict(res.data.has_conflict);
        setHasCooperation(res.data.has_cooperation);
        setConflictMatrixExists(res.data.has_conflict || res.data.has_cooperation);
      } catch (err) {
        setHasConflict(false);
        setHasCooperation(false);
        setConflictMatrixExists(false);
        setConflictError("Could not fetch matrix status.");
      }
    }

    checkConflictMatrix();
  }, [userId]);

  const handleExport = () => {
    let output = `Role Assignments for ${user.COMPANY_NAME} – ${user.DEPARTMENT}\n\n`;

    roles.forEach((role, colIdx) => {
      const assignedAgents = agents
        .filter((_, rowIdx) => matrix?.[rowIdx]?.[colIdx] === 1)
        .map(agent => `${agent.FIRST_NAME} ${agent.LAST_NAME}`);

      if (assignedAgents.length > 0) {
        output += `${role.ROLE_NAME}:\n`;
        assignedAgents.forEach(agentName => {
          output += `  - ${agentName}\n`;
        });
        output += '\n';
      }
    });

    const blob = new Blob([output], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `GMRA_Assignment_${user.COMPANY_NAME}_${user.DEPARTMENT}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading) return <div>Loading Assignment Matrix...</div>;
  if (!userId) return <div>Error: Missing user ID</div>;

  return (
    <div>
      <h2>
        Group Multi-Role Assignment Results
      </h2>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem" }}>
        <button
          className="upload-button"
          style={{
            backgroundColor: hasConflict ? "#cf2525" : "#888",
            color: "#fff",
            cursor: hasConflict ? "pointer" : "not-allowed",
            pointerEvents: hasConflict ? "auto" : "none"
          }}
          onClick={() => handleConsiderMatrix(false)}
        >
          Consider Conflicts
        </button>

        <button
          className="upload-button"
          style={{
            backgroundColor: hasCooperation ? "rgb(24, 136, 24)" : "#888",
            color: "#fff",
            cursor: hasCooperation ? "pointer" : "not-allowed",
            pointerEvents: hasCooperation ? "auto" : "none"
          }}
          onClick={() => handleConsiderMatrix(true)}
        >
          Consider Cooperation and Conflicts
        </button>
      </div>

        {!conflictMatrixExists && (
          <div style={{ marginTop: "0.5rem", color: "#555", fontStyle: "italic" }}>
            Please identify agent statuses by clicking the "Agent Statuses" section of the account options
          </div>
        )}
      
      
      <div className="text-section">
        <table className="evaluation-table">
          <thead>
            <tr>
              <th className="diagonal-header">
                <div className="top-left-text">Roles</div>
                <div className="bottom-right-text">Agents</div>
              </th>
              {roles.map((role) => (
                <th key={role.ROLE_NAME}>{role.ROLE_NAME}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {agents.map((agent, rowIdx) => {
              const agentKey = agent.AGENT_NUM;
              return (
                <tr key={agentKey}>
                  <td>{agent.FIRST_NAME} {agent.LAST_NAME}</td>
                  {roles.map((role, colIdx) => {
                    const score = evaluations?.[agentKey]?.[role.ROLE_NAME] ?? 0;
                    const isAssigned = matrix?.[rowIdx]?.[colIdx] === 1;

                    return (
                      <td
                        key={role.ROLE_NAME}
                        style={{
                          backgroundColor: isAssigned ? "#5a4864" : "transparent",
                          color: isAssigned ? "#ffffff" : "#000000"
                        }}
                      >
                        {score.toFixed(2)}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
        <div className="button-box">
          <button className="upload-button" style={{ marginLeft: "1rem" }} onClick={handleExport}>
            Export Results
          </button>
          <Link to="../assignment/GMRA1">
              <button className="upload-button" style={{ backgroundColor: "#ccc"}} >Return to Assignment Setup</button>
          </Link>
      </div>
      </div>
    </div>
  );
};

export default GMRAMatrixPage;
