import { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/agent_statuses.css";

const AgentStatusesPage = ({ userId }) => {
  const [agents, setAgents] = useState([]);
  const [statusMatrix, setStatusMatrix] = useState([]);
  const [mode, setMode] = useState("cooperation"); // "cooperation" or "conflict"
  const [viewMode, setViewMode] = useState("gradient"); // "gradient" or "binary"
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAgentsAndConflicts() {
      try {
        setLoading(true);
        const res = await axios.get(
          `/api/assignments/agents_with_conflicts/${userId}?mode=${viewMode}`
        );
        const agentList = res.data.agents || [];
        const conflicts = res.data.conflicts || [];
        const agentNumToIndex = {};
        agentList.forEach((agent, idx) => {
          agentNumToIndex[agent.AGENT_NUM] = idx;
        });

        let matrix;
        if (viewMode === "gradient") {
          matrix = Array(agentList.length)
            .fill()
            .map(() => Array(agentList.length).fill(0));
          conflicts.forEach(({ AGENT_NUM_1, AGENT_NUM_2, CONFLICT_VALUE }) => {
            const i = agentNumToIndex[AGENT_NUM_1];
            const j = agentNumToIndex[AGENT_NUM_2];
            const val = parseFloat(CONFLICT_VALUE);
            if (!isNaN(val)) {
              matrix[i][j] = val;
              matrix[j][i] = val;
            }
          });
        } else {
          matrix = Array(agentList.length)
            .fill()
            .map(() => Array(agentList.length).fill(false));
          conflicts.forEach(({ AGENT_NUM_1, AGENT_NUM_2 }) => {
            const i = agentNumToIndex[AGENT_NUM_1];
            const j = agentNumToIndex[AGENT_NUM_2];
            matrix[i][j] = true;
            matrix[j][i] = true;
          });
        }

        setAgents(agentList);
        setStatusMatrix(matrix);
      } catch (err) {
        console.error("Failed to fetch agents or conflicts", err);
      } finally {
        setLoading(false);
      }
    }

    fetchAgentsAndConflicts();
  }, [userId, viewMode]);

  const handleGradientCellClick = (i, j) => {
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

  const handleBinaryCellClick = (i, j) => {
    if (i === j) return;
    const newValue = !statusMatrix[i][j];
    const updated = statusMatrix.map((row, rowIndex) =>
      row.map((cell, colIndex) => {
        if ((rowIndex === i && colIndex === j) || (rowIndex === j && colIndex === i)) {
          return newValue;
        }
        return cell;
      })
    );
    setStatusMatrix(updated);
  };

  const handleSubmit = async () => {
    const conflictData = [];

    for (let i = 0; i < agents.length; i++) {
      for (let j = i + 1; j < agents.length; j++) {
        const val = statusMatrix[i][j];
        if (viewMode === "gradient") {
          if (val !== 0) {
            conflictData.push({
              AGENT_NUM_1: agents[i].AGENT_NUM,
              AGENT_NUM_2: agents[j].AGENT_NUM,
              CONFLICT_VALUE: parseFloat(val),
            });
          }
        } else {
          if (val === true) {
            conflictData.push({
              AGENT_NUM_1: agents[i].AGENT_NUM,
              AGENT_NUM_2: agents[j].AGENT_NUM,
              CONFLICT_VALUE: 1.0,
            });
          }
        }
      }
    }

    try {
      await axios.post(`/api/assignments/conflicts/${userId}`, {
        conflicts: conflictData,
        mode: viewMode,
      });
      alert("Matrix submitted successfully!");
    } catch (err) {
      console.error("Failed to submit matrix", err);
      alert("Submission failed.");
    }
  };

  const getGradientStyle = (value) => {
    const val = parseFloat(value);
    if (!isFinite(val)) return {};
    if (val > 0) return { backgroundColor: `rgba(0, 200, 0, ${val})` };
    if (val < 0) return { backgroundColor: `rgba(255, 0, 0, ${-val})` };
    return {};
  };

  if (loading) return <div>Loading matrix...</div>;

  if (agents.length <= 1) {
    return (
      <div>
        <h2>Agent Status Matrix</h2>
        <p className="text"> You may define relationships within your team. Conflict only mode allows you to designate absolute conflict. That is to say - 
            when evaluating with conflicts only, agents in conflict will not work the same role together. In Conflict and Cooperation mode, you may 
            scale the matrix to represent your real-world environemnt to provide more optimal results.
        </p>
        <h2 className="text">
          No agents found. Please add agents to view or edit the matrix.
        </h2>
      </div>
    );
  }

  return (
    <div>
      <div className="header-row">
        <h2>Agent Status Matrix</h2>
        <p className="text"> You may define relationships within your team. Conflict only mode allows you to designate absolute conflict. That is to say - 
          when evaluating with conflicts only, agents in conflict will not work the same role together. In Conflict and Cooperation mode, you may 
          scale the matrix to represent your real-world environemnt to provide more optimal results.</p>
        <div className="mode-switch">
          <label className="switch-label">Conflict only</label>
          <label className="switch">
            <input
              type="checkbox"
              checked={viewMode === "gradient"}
              onChange={() => setViewMode((prev) => (prev === "gradient" ? "binary" : "gradient"))}
            />
            <span className="slider round"></span>
          </label>
          <label className="switch-label">Conflict and Cooperation</label>
        </div>
      </div>

      <div className="evaluation-container">
        <table className="status-matrix">
          <thead>
            <tr>
              <th></th>
              {agents.map((agent, index) => (
                <th key={index}>
                  {agent.FIRST_NAME} {agent.LAST_NAME}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {agents.map((agent, i) => (
              <tr key={i}>
                <td>
                  <strong>
                    {agent.FIRST_NAME} {agent.LAST_NAME}
                  </strong>
                </td>
                {agents.map((_, j) => {
                  if (viewMode === "gradient") {
                    return (
                      <td
                        key={j}
                        className={i === j ? "disabled-cell" : "status-cell"}
                        style={getGradientStyle(statusMatrix[i]?.[j])}
                        title={statusMatrix[i]?.[j]}
                        onClick={() => handleGradientCellClick(i, j)}
                      />
                    );
                  } else {
                    return (
                      <td
                        key={j}
                        className={i === j ? "disabled-cell" : statusMatrix[i][j] ? "active-cell" : ""}
                        onClick={() => handleBinaryCellClick(i, j)}
                      />
                    );
                  }
                })}
              </tr>
            ))}
          </tbody>
        </table>

        {viewMode === "gradient" && (
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
        )}

        <div className="button-box">
          <button className="upload-button" onClick={handleSubmit}>
            Submit Matrix
          </button>
        </div>
      </div>
    </div>
  );
};

export default AgentStatusesPage;