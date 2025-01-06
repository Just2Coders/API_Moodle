Moodle Api
This project develops an API that serves as a gateway between Moodle and an external website, enabling seamless communication and efficient management of training services for XETID personnel. The API is designed to be robust, secure, and efficient, utilizing modern technologies like FastAPI and adapting to Moodle's web services.

📚 Key Features
Moodle Service Access: Provides endpoints to interact with essential Moodle functionalities, such as course, user, and category management.
Secure Authentication: Implements authentication based on administrator and user tokens.
Extensibility: Designed to support future modules and features without disrupting the current structure.
Standards Compliance: Adheres to software engineering principles.
🚀 Technologies Used
Backend: FastAPI (Python)
Database: PostgreSQL (via Moodle's web services)
Integration: Moodle's native web services
📋 Installation
Prerequisites
Install Python 3.9+.
Access a configured Moodle instance.
Install PostgreSQL (optional if directly using Moodle’s database).
Steps
Clone the repository:

bash
Copiar código
git clone https://github.com/Just2Coders/API_Moodle.git
cd your-repository
Create a virtual environment and install dependencies:

bash
Copiar código
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
Configure environment variables in a .env file (example provided in .env.example):

env
Copiar código
MOODLE_URL=https://your-moodle.com
MOODLE_ADMIN_TOKEN=your_admin_token
DATABASE_URL=postgresql://user:password@localhost:port/your_database
Run the server:

bash
Copiar código
uvicorn app.main:app --reload
Access the interactive documentation at http://127.0.0.1:8000/docs.

🔑 Main Endpoints
Authentication
Get User Token:
POST /auth/token
Parameters: User credentials.
Response: JWT token for authenticated access.

🛠️ Development
Project Structure
plaintext
Copiar código
├── app/
│   ├── main.py         # Application entry point
│   ├── routes/         # Endpoints organized by modules
│   ├── models/         # Data model definitions
│   ├── services/       # Business logic and Moodle connection
│   ├── tests/          # Automated tests
├── requirements.txt    # Project dependencies
├── .env.example        # Example configuration
└── README.md           # Documentation

✉️ Contact
Author: [marlonjb]
Email: [marlonmarrerorodriguez@gmail.com]
