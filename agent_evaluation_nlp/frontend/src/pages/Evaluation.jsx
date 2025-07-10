import { useEffect, useState } from "react";
import { Download, FileSearch, FileSpreadsheet } from "lucide-react";
import axios from "axios";
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import '../styles/evaluation.css';

const Evaluation = ({ userId }) => {
  const [user, setUser] = useState(null);
  const [agents, setAgents] = useState([]);
  const [roles, setRoles] = useState([]);
  const [evaluations, setEvaluations] = useState({});
  const [originalEvaluations, setOriginalEvaluations] = useState({});
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const evalResponse = await axios.get(`/api/evaluations/${userId}`);
        setAgents(evalResponse.data.agents || []);
        setRoles(evalResponse.data.roles || []);
        setEvaluations(evalResponse.data.evaluations || {});
        setOriginalEvaluations(evalResponse.data.evaluations || {});
        setUser(evalResponse.data.user || {});
      } catch (error) {
        console.error("Error loading data", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [userId]);

  const sanitize = (str) =>
    str?.replace(/\s+/g, "-").replace(/[^\w\-]/g, "") || "unknown";

  const handleEvaluate = async () => {
    setLoading(true);
    try {
      await axios.post(`/api/evaluations/${userId}`, agents, {
        headers: { "Content-Type": "application/json" },
      });
      alert("Agents evaluated successfully!");
      window.location.reload();
    } catch (error) {
      console.error("Failed to evaluate agents", error);
      alert("Error evaluating agents.");
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluationChange = (agentNum, role, value) => {
    let parsed = parseFloat(value);
    if (isNaN(parsed)) parsed = 0;
    parsed = Math.max(0, Math.min(1, parsed)); // clamp to [0, 1]

    setEvaluations((prev) => ({
      ...prev,
      [agentNum]: {
        ...prev[agentNum],
        [role]: parsed,
      },
    }));
  };
  
  const handleSaveEvaluations = async () => {
    try {
      // Clamp all evaluation values to [0, 1]
      const clampedEvaluations = Object.fromEntries(
        Object.entries(evaluations).map(([agentNum, roleScores]) => [
          agentNum,
          Object.fromEntries(
            Object.entries(roleScores).map(([role, score]) => [
              role,
              Math.max(0, Math.min(1, parseFloat(score) || 0)),
            ])
          ),
        ])
      );

      await axios.put(`/api/evaluations/${userId}`, { evaluations: clampedEvaluations }, {
        headers: { "Content-Type": "application/json" },
      });

      alert("Evaluations updated successfully!");
      setEditMode(false);
      setOriginalEvaluations(clampedEvaluations);  // Update the original with clamped values
    } catch (error) {
      console.error("Update failed:", error);
      alert("Error updating evaluations.");
    }
  };

  const handleCancelEdit = () => {
    setEvaluations(originalEvaluations);
    setEditMode(false);
  };

  const exportToCSV = () => {
    const headers = ['Agents', ...roles];
    const rows = agents.map(agent => {
      const row = [`${agent.FIRST_NAME} ${agent.LAST_NAME}`];
      roles.forEach(role => {
        const score = evaluations[agent.AGENT_NUM]?.[role] ?? 0;
        row.push(score);
      });
      return row;
    });

    const csvContent = [headers, ...rows].map(e => e.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const fileName = `${sanitize(user?.COMPANY_NAME)}-${sanitize(user?.DEPARTMENT)}-evaluation`;
    link.href = url;
    link.download = `${fileName}.csv`;
    link.click();
  };

  const exportToExcel = () => {
    const data = agents.map(agent => {
      const row = { Agents: `${agent.FIRST_NAME} ${agent.LAST_NAME}` };
      roles.forEach(role => {
        row[role] = evaluations[agent.AGENT_NUM]?.[role] ?? 0;
      });
      return row;
    });

    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Evaluations");

    const excelBuffer = XLSX.write(workbook, { bookType: "xlsx", type: "array" });
    const blob = new Blob([excelBuffer], { type: "application/octet-stream" });
    const fileName = `${sanitize(user?.COMPANY_NAME)}-${sanitize(user?.DEPARTMENT)}-evaluation`;
    saveAs(blob, `${fileName}.xlsx`);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Agent-Role Evaluation</h2>
        {agents.length === 0 || roles.length === 0 ? (
            <p></p>
          ) : !editMode ? (
            <button className="upload-button" onClick={() => setEditMode(true)} disabled={loading}>
              Modify
            </button>
          ) : (
            <div className="button-box">
              <button className="upload-button" onClick={handleSaveEvaluations}>Save</button>
              <button
                className="upload-button"
                onClick={handleCancelEdit}
                style={{ marginLeft: '0.5rem', backgroundColor: '#ccc' }}
              >
                Cancel
              </button>
            </div>
          )}
      </div>

      <div className="evaluation-container">
        {agents.length === 0 || roles.length === 0 ? (
          <div className="missing-info">
            <h2 className="text">
              Missing information - Agents or roles are not properly defined. Please ensure both are defined before evaluation.
            </h2>
          </div>
        ) : (
          <>
            <table className="evaluation-table">
              <thead>
                <tr>
                  <th className="diagonal-header">
                    <div className="top-left-text">Roles</div>
                    <div className="bottom-right-text">Agents</div>
                  </th>
                  {roles.map(role => (
                    <th key={role}>{role}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {agents.map(agent => (
                  <tr key={agent.AGENT_NUM}>
                    <td>{agent.FIRST_NAME} {agent.LAST_NAME}</td>
                    {roles.map(role => (
                      <td key={role}>
                        {editMode ? (
                          <input
                            type="number"
                            step="0.01"
                            min="0"
                            max="1"
                            value={evaluations[agent.AGENT_NUM]?.[role]?.toFixed(2) ?? 0}
                            onChange={(e) =>
                              handleEvaluationChange(agent.AGENT_NUM, role, e.target.value)
                            }
                            className="editable-cell"
                          />
                        ) : (
                          (evaluations[agent.AGENT_NUM]?.[role]?.toFixed(2) ?? "0.00")
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>

            {!editMode && (
              <div className="button-box">
                <div className="evaluate-section">
                  <button
                    className="upload-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEvaluate();
                    }}
                    disabled={loading}
                  >
                    {loading ? "Evaluating..." : (
                      <>
                        Evaluate { <FileSearch size={20} /> }
                      </>
                    )}
                  </button>
                </div>
                <p>Export as:</p>
                <div className="export-section">
                  <div className="spacer-vertical">
                    <button
                      className="upload-button"
                      onClick={(e) => {
                        e.stopPropagation();
                        exportToCSV();
                      }}
                    >
                      <>
                        CSV { <Download size={20} /> }
                      </>
                    </button>
                    <button
                      className="upload-button"
                      onClick={(e) => {
                        e.stopPropagation();
                        exportToExcel(); 
                      }}
                    >
                      <>
                        Excel { <FileSpreadsheet size={20} /> }
                      </>
                    </button>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Evaluation;
