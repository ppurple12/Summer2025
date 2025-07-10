import React, { useState } from "react";
import axios from "axios";
import { Import, Upload} from "lucide-react";
import { Link } from "react-router-dom";
import "../styles/docs.css";

function FileUploader({userId}) {
  const [files, setFiles] = useState([]);
  const [uploadResult, setUploadResult] = useState(null);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
  };

 const uploadFiles = async () => {
    const formData = new FormData();
    for (let file of files) {
      formData.append("files", file);
    }

    try {
      const response = await axios.post(`/api/upload-folder/${userId}`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setUploadResult(response.data); // Save the result for rendering
      setFiles([]); // Optional: clear files after upload
    } catch (error) {
      console.error("Upload error:", error);
      setUploadResult({ error: "Upload failed. Please try again." });
    }
  };

  return (
    <div>
      <h2>Documents</h2>
      <div className="upload-container">
      <p className="text">
        Import all relevent documentation here. If the document does not include agent names or agent ID,
        consider adding them for better results.
      </p>
      <div
        className="upload-box"
        onClick={() => document.getElementById("fileInput").click()}
      >
        {files.length > 0 && (
          <div className="file-list">
            <h4>Selected Files:</h4>
            <ul>
              {files.map((file, index) => (
                <li key={index}>{file.name}</li>
              ))}
            </ul>
          </div>
        )}

        <Import className="upload-icon" />
        <p>Upload documents here</p>

        <input
          id="fileInput"
          type="file"
          multiple
          onChange={handleFileChange}
          className="file-input"
          style={{ display: "none" }}
        />
      </div>

      <div className="button-box">
        <button
          className="upload-button"
          onClick={() => document.getElementById("fileInput").click()}
        >
          Import
          <Import size = {20} />
        </button>
        <button
          className="upload-button"
          onClick={(e) => {
            e.stopPropagation();
            uploadFiles();
          }}
        >
          Upload
         <Upload size = {20}/>
        </button>
        </div>
      </div>
    

      {uploadResult && (
  <div className="upload-result">
    {uploadResult.error ? (
      <p className="error">{uploadResult.error}</p>
    ) : (
      <>
        <p>{uploadResult.inserted_count} new documents inserted. If this is less then expected, please make sure your documents can identify pertinent agents</p>
        {uploadResult.skipped_duplicates?.length > 0 && (
          <div>
            <p>Skipped {uploadResult.skipped_duplicates.length} duplicate entries:</p>
            <ul>
              {uploadResult.skipped_duplicates.map((entry, index) => (
                <li key={index}>
                  {entry.agent_name} ({entry.category}) – {entry.reason}
                </li>
              ))}
            </ul>
          </div>
        )}
      </>
    )}
  </div>
)}
    <div className="spacer" />
        <Link to="/evaluation" className="button-container">
          <button className="proceed-button"> Proceed to Agent Evaluation </button>
        </Link>
    </div>
  );
}

export default FileUploader;
