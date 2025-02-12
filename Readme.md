# 🚀 RE-Miner Dashboard BFF

The **RE-Miner Dashboard BFF** serves as backend and core processing unit for the **RE-Miner 2.0**.

It handles the API requests, data processing, user management and integration with the other components within the RE-Miner 2.0 architecture: 

![RE-Miner-2.0](/static/images/RE-Miner-2.0.png)


## 📖 Table of Contents

- [⚙️ Architecture](#️-architecture)
- [📌 Prerequisites](#-prerequisites)
- [📦 Installation](#-installation)
  - [Manual Installation](#manual-installation)
  - [Docker Installation](#docker-installation)
- [Usage](#-usage)
- [🚀 How to Deploy](#-how-to-deploy)
  - [Manual Deployment](#manual-deployment)
  - [Docker Deployment](#docker-deployment)
- [📜 License](#-license)
- [🔗 Contact](#-contact)

---

## ⚙️ Architecture

The **RE-Miner Backend** is designed with a modular architecture to ensure scalability and maintainability. It comprises:

📌 **API Module** – Handles incoming HTTP requests and routes them to appropriate services. The API module is structured into various **routes**, each responsible for a specific feature of the system:

| **Route**         | **Description** |
|-------------------|---------------|
| **Authentication (`auth_routes.py`)** | Manages user login, registration, authentication, token refresh, and logout. |
| **User Management (`user_routes.py`)** | Handles user creation, retrieval, updating, and deletion. |
| **Review Management (`review_routes.py`)** | Allows users to submit, retrieve, update, and delete app reviews. Also supports review filtering and analysis. |
| **Application Management (`application_routes.py`)** | Manages mobile applications, their metadata, and associated features. |
| **Analysis (`analysis_routes.py`)** | Provides sentiment analysis, feature extraction, and NLP-based review insights. |
| **Tree Processing (`tree_routes.py`)** | Handles hierarchical clustering, feature trees, and structured representations of app reviews. |
| **Filtering & Search (`filter_routes.py`)** | Enables advanced filtering and searching of user reviews based on feature sets, topics, emotions, and sentiment polarity. |
| **Health Check (`health_routes.py`)** | Exposes a `/ping` endpoint to verify API availability and system health. |

---

📌 **Authentication Module** – Manages user authentication and authorization, ensuring secure access to API endpoints.  
🔗 **[See Authentication Module README](authentication_module/README.md)**  

📌 **Processing Module** – Coordinates feature extraction and emotion classification tasks by interfacing with external services like **RE-Miner Hub**.  

📌 **Database Module** – Manages interactions with the **SQL database** for **data persistence**. It handles user information, reviews, applications, and analysis results.  


## Prerequisites

Before setting up the RE-Miner Backend, ensure you have the following installed:

- **Python 3.9**  
- **pip** (Python package manager)  
- **Docker** (for containerized deployment)  
- **Git** (for version control)  

---

## 📦 Installation

### **Manual Installation**
1) **Clone the Repository**  

```bash
git clone https://github.com/gessi-chatbots/RE-Miner-Backend.git
cd RE-Miner-Backend
```

2) **Set Up a Virtual Environment**  

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3) **Install Dependencies**  

```bash
pip install -r requirements.txt
```

---

### **Docker Installation**
For a quicker setup, you can use Docker.

1) **Build the Docker Image**  

```bash
docker build -t re-miner-backend .
```

2) **Run the Docker Container**  

```bash
docker run -d -p 3005:3005 --env-file=backend.env re-miner-backend
```

---

## Usage

To start the backend server manually:

```bash
flask run --port=3005
```

The API will be available at: `http://localhost:3005`

Use **Postman** or `curl` to test the API endpoints.

---

## 🚀 How to Deploy

### **Manual Deployment**
For production, use **Gunicorn** for performance:

```bash
gunicorn -w 4 -b 0.0.0.0:3005 app:app
```

### **Docker Deployment**
Deploy using Docker for easy scalability:

```bash
docker build -t re-miner-backend .
docker run -d -p 3005:3005 --env-file=backend.env re-miner-backend
```

---
## 📜 License

This project is licensed under the **[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html)**.  
For more details, see the [`LICENSE`](LICENSE) file.

---

🔗 **Developed by [GESSI - NLP4SE](https://gessi.upc.edu/en/research-areas/nlp4se)**  
