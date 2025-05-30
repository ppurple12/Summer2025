# Using Natural Language Processing for Agent Evaluation  
### Requirement Report 
**Author:** Evan Wells  


## Introduction

This requirement report includes the reasoning as well as the necessity for numerous components of the project. As the design framework and requirement analysis showcase, the project can be divided into the following components:

- Input/File Handling  
- Data Processing  
- Frontend  
- Backend  
- Databases  
- Training/Data Labelling  
- Modelling/NLP  
- Output

---

## Final Product

Before analyzing the individual components, we must observe the requirements of the final product. The product – a system that evaluates agents on specified roles using agent documentation – is crucial to managers. With this, they can better evaluate agents, in attempts to optimize their respective environments. 

This aids specifically within the **Role Based Collaboration**, where the provided evaluation can easily be treated as a complete **Q matrix**. Essentially, managers can utilize this software to objectively, quickly and accurately evaluate their staff for the roles of their choosing. With proper supporting documentation, this can provide a holistic evaluation of the agents.

---

## Component Requirements

| Components       | Requirements                                                                                                                                                        | Method                                                                                                            | Why?                                                                                                                                                                                                                                      |
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **File Handling** | To properly analyze documents and prepare for NLP, the File Handling mechanisms must be pristine. Without them, the documents will not properly be loaded and separated. A general format followed by all file types simplifies the following components, mainly data preprocessing. | - Pipeline                                                                                                        | Using a pipeline to handle file inputs depending on file type will ensure consistent loading across formats and prevent unnecessary errors. More file types can be added to promote generality.                                           |
| **Data Processing** | Data Preprocessing consists of taking the files provided by the manager and preparing them as much as possible before storing. These preprocessing steps include stripping the text, removing unnecessary filler words, such as “if” or “the”. It also includes associating the proper agent to the text. This allows easy access to proper documentation during the evaluation process. | - FAISS<br>- Sentence Transformer                                                                                 | FAISS (Facebook AI Semantic Search) is used to find agent names or near matches (e.g., “Dr. Mike”) to associate the proper agents with the proper text. Sentence Transformer and general Python functions are used to create word embeddings. |
| **Frontend**      | A simplistic and intuitive UI is crucial to a successful application. The key is to have good interaction between the frontend and the backend. To reduce resources, no framework will be used to bridge the gap between them. This adds complexity but benefits users. | - React Vite                                                                                                     | React Vite is a very proficient and easy-to-use framework for designing dynamic frontend pages. It is open-sourced, highly used and documented.                                                                                           |
| **Backend**       | The backend must ensure data is properly loaded, organized, and computed. When dealing with Big Data, it is important that the backend is efficient in its querying and that the data models/schemas are well defined. | - FastAPI                                                                                                         | FastAPI is lightweight and more scalable than Flask. It has less overhead and works efficiently with both databases and the frontend.                                                                                                    |
| **Database**      | The organization of the database is crucial. A hybrid approach is optimal: relational data in MySQL and unstructured/semi-structured data in MongoDB. This supports optimal access and performance. | - MySQL<br>- MongoDB                                                                                              | MySQL supports relational data with SQL queries. MongoDB handles unstructured data and has scalable collections with large data blocks.                                                                                                    |
| **Training**      | The training process must be efficient and thorough. Bootstrap methods, cross-validation, and semantic matching are necessary. Large, diverse data prevents bias and overfitting. | - SpaCy<br>- Kaggle                                                                                               | SpaCy is an industrial-grade NLP library. Kaggle offers robust datasets in various formats for training.                                                                                                                               |
| **Modelling/NLP** | The model uses a combination of pretrained models (XGBoost), semantic embeddings (FAISS), and sentiment analysis to achieve accurate evaluations. | - FAISS<br>- NLTK Sentiment Analysis<br>- XGBoost                                                                | Sentiment analysis (via NLTK) helps interpret feedback and HR documents. XGBoost allows efficient training for regression models.                                                                                                         |
| **Output**        | The output is the Q matrix for given agents and roles. This matrix will be exportable (CSV/Excel). Optional: generate GRA on request using a Role Range Vector (L). | - TBD                                                                                                             | Exporting gives users flexibility. Advanced GRA options (GRA+, GMRA) may be added later based on user needs.                                                                                                                             |

---

## Conclusion

Overall, the requirements can be seen as all crucial, with each component being its own project to work on. With all these requirements reached, the final product will be an efficient, accurate, and innovative approach to **Agent Evaluation**.
