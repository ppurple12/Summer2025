import { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/agent_statuses.css";

const AgentStatusesPage = ({ userId }) => {
  const [agents, setAgents] = useState([]);
  const [statusMatrix, setStatusMatrix] = useState([]);
  const [mode, setMode] = useState("cooperation");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAgentsAndConflicts() {
      try {
        const res = await axios.get(`/api/assignments/agents_with_conflicts/${userId}`);
        const agentList = res.data.agents || [];
        const conflicts = res.data.conflicts || [];

        const agentNumToIndex = {};
        agentList.forEach((agent, idx) => {
          agentNumToIndex[agent.AGENT_NUM] = idx;
        });

        const initialMatrix = Array(agentList.length)
          .fill()
          .map(() => Array(agentList.length).fill(0));

        conflicts.forEach(({ AGENT_NUM_1, AGENT_NUM_2, CONFLICT_VALUE }) => {
          const i = agentNumToIndex[AGENT_NUM_1];
          const j = agentNumToIndex[AGENT_NUM_2];
          const val = parseFloat(CONFLICT_VALUE);

          if (i !== undefined && j !== undefined && !isNaN(val)) {
            initialMatrix[i][j] = val;
            initialMatrix[j][i] = val;
          }
        });

        setAgents(agentList);
        setStatusMatrix(initialMatrix);
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch agents or conflicts", err);
      }
    }

    fetchAgentsAndConflicts();
  }, [userId]);

  const handleCellClick = (i, j) => {
    if (i === j) return;

    setStatusMatrix((prev) => {
      const updated = prev.map((row) => [...row]);
      const current = parseFloat(updated[i][j]) || 0;
      let newVal = current;

      if (mode === "cooperation") {
        newVal = current >= 1 ? 0 : Math.min(current + 0.2, 1);
      } else {
        newVal = current <= -1 ? 0 : Math.max(current - 0.2, -1);
      }

      newVal = parseFloat(newVal.toFixed(2));
      updated[i][j] = newVal;
      updated[j][i] = newVal;
      return updated;
    });
  };

  const handleSubmit = async () => {
    const matrixData = [];

    for (let i = 0; i < agents.length; i++) {
      for (let j = i + 1; j < agents.length; j++) {
        const val = parseFloat(statusMatrix[i][j]);
        if (val !== 0) {
          matrixData.push({
            AGENT_NUM_1: agents[i].AGENT_NUM,
            AGENT_NUM_2: agents[j].AGENT_NUM,
            CONFLICT_VALUE: val,
          });
        }
      }
    }

    try {
      await axios.post(`/api/assignments/conflicts/${userId}`, { conflicts: matrixData });
      alert("Matrix submitted successfully!");
    } catch (err) {
      console.error("Failed to submit matrix", err);
      alert("Submission failed.");
    }
  };

  const getCellStyle = (value) => {
    const val = parseFloat(value);
    if (val > 0) return { backgroundColor: `rgba(0, 200, 0, ${val})` };
    if (val < 0) return { backgroundColor: `rgba(255, 0, 0, ${-val})` };
    return {};
  };

  if (loading) return <div>Loading matrix...</div>;

  return (
    <div>
      <h2>Agent Cooperation & Conflict Matrix</h2>
      <div className="evaluation-container">
        <table className="status-matrix">
          <thead>
            <tr>
              <th></th>
              {agents.map((agent, index) => (
                <th key={index}>{agent.FIRST_NAME} {agent.LAST_NAME}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {agents.map((agent, i) => (
              <tr key={i}>
                <td><strong>{agent.FIRST_NAME} {agent.LAST_NAME}</strong></td>
                {agents.map((_, j) => (
                  <td
                    key={j}
                    className={i === j ? "disabled-cell" : "status-cell"}
                    style={getCellStyle(statusMatrix[i]?.[j])}
                    onClick={() => handleCellClick(i, j)}
                  />
                ))}
              </tr>
            ))}
          </tbody>
        </table>

        <div className="legend-box">
          <button
            className={`legend-button ${mode === "cooperation" ? "active" : ""}`}
            onClick={() => setMode("cooperation")}
          >
            🟢 Cooperation
          </button>
          <button
            className={`legend-button ${mode === "conflict" ? "active" : ""}`}
            onClick={() => setMode("conflict")}
          >
            🔴 Conflict
          </button>
        </div>

        <div className="button-box">
          <button className="upload-button" onClick={handleSubmit}>Submit Matrix</button>
        </div>
      </div>
    </div>
  );
};

export default AgentStatusesPage;