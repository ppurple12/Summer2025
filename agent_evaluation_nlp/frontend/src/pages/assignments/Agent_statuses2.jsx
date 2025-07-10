import { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/agent_statuses.css";

const AgentStatusesPage = ({ userId }) => {
  const [agents, setAgents] = useState([]);
  const [statusMatrix, setStatusMatrix] = useState([]);

  useEffect(() => {
    async function fetchAgentsAndConflicts() {
      try {
        const res = await axios.get(`/api/assignments/agents_with_conflicts/${userId}`);
        const agentList = res.data.agents || [];
        const conflicts = res.data.conflicts || [];

        setAgents(agentList);

        // Create index map from AGENT_NUM to matrix indices
        const agentNumToIndex = {};
        agentList.forEach((agent, idx) => {
          agentNumToIndex[agent.AGENT_NUM] = idx;
        });

        // Initialize empty matrix
        const initialMatrix = Array(agentList.length)
          .fill()
          .map(() => Array(agentList.length).fill(false));

        // Fill in the matrix with existing conflicts
        conflicts.forEach(({ AGENT_NUM_1, AGENT_NUM_2 }) => {
          const i = agentNumToIndex[AGENT_NUM_1];
          const j = agentNumToIndex[AGENT_NUM_2];
          if (i !== undefined && j !== undefined) {
            initialMatrix[i][j] = true;
            initialMatrix[j][i] = true; // Symmetric
          }
        });

        setStatusMatrix(initialMatrix);
      } catch (err) {
        console.error("Failed to fetch agents or conflicts", err);
      }
    }

    fetchAgentsAndConflicts();
  }, [userId]);

  const toggleCell = (i, j) => {
    if (i === j) return;
    const newValue = !statusMatrix[i][j];
    const updated = statusMatrix.map((row, rowIndex) =>
      row.map((cell, colIndex) => {
        if (
          (rowIndex === i && colIndex === j) ||
          (rowIndex === j && colIndex === i)
        ) {
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
        if (statusMatrix[i][j]) {
          conflictData.push({
            AGENT_NUM_1: agents[i].AGENT_NUM,
            AGENT_NUM_2: agents[j].AGENT_NUM,
            CONFLICT_VALUE: 1.0,
          });
        }
      }
    }

    try {
      await axios.post(`/api/assignments/conflicts/${userId}`, { conflicts: conflictData });
      alert("Conflicts submitted successfully!");
    } catch (err) {
      console.error("Failed to submit conflicts", err);
      alert("Failed to submit conflicts.");
    }
  };

  return (
    <div>
      <h2>Agent Conflict Matrix</h2>
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
                  className={
                    i === j
                      ? "disabled-cell"
                      : statusMatrix[i][j]
                      ? "active-cell"
                      : ""
                  }
                  onClick={() => toggleCell(i, j)}
                ></td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      <div className="button-box">
        <button
          className="upload-button"
          style={{ marginTop: "1rem" }}
          onClick={handleSubmit}
        >
          Submit Conflicts
        </button>
        </div>
      </div>
    </div>
  );
};

export default AgentStatusesPage;