# ClariMed

⸻

🩺 ClariMed — Making Medical Documents Clear, Simple, and Actionable

ClariMed is an AI-powered web platform that transforms confusing medical documents — like hospital discharge summaries, lab reports, or clinical notes — into clear, understandable, multilingual explanations that patients and caregivers can trust.

ClariMed breaks down complex jargon into plain-language summaries, highlights critical red-flag warnings, provides next-step action plans, defines medical terms, and can even read the results aloud — empowering people to make informed healthcare decisions with confidence.

⸻

🚀 Key Features
	•	📤 Upload PDFs or Scans – Drag and drop any medical document for instant analysis.
	•	🔍 AI-Powered OCR & Understanding – Extract and interpret text using Google Cloud Vision and Gemini.
	•	🧠 Plain-Language Summaries – Convert clinical language into easy-to-read explanations (6th–8th grade level).
	•	📋 Actionable Insights – Automatically generate a “What to do next” checklist and highlight red-flag symptoms.
	•	📚 Medical Glossary – Define technical terms clearly and contextually.
	•	🌎 Multilingual Support – Translate entire reports into other languages (like Spanish) in one click.
	•	🔊 Voice Narration (Optional) – Hear summaries read aloud with natural-sounding AI voices.
	•	☁️ Secure & Scalable – Built with Google Cloud, Snowflake, and ElevenLabs for safety and performance.

⸻

🧰 Tech Stack

🖥️ Frontend
	•	⚛️ React.js – Component-based UI and user experience
	•	🎨 Tailwind CSS / Material UI – Modern, responsive design
	•	📡 Axios – REST API communication with Flask backend

🔧 Backend
	•	🐍 Flask (Python) – REST API backend and orchestration
	•	☁️ Google Cloud Storage – Secure file storage and access
	•	🔍 Google Cloud Vision – Optical Character Recognition (OCR) for text extraction
	•	🧠 Gemini API (Google) – Text summarization, simplification, and translation
	•	🗄️ Snowflake – Glossary, term definitions, and contextual medical knowledge retrieval
	•	🔊 ElevenLabs (Optional) – Natural-sounding text-to-speech narration

⸻

🧪 How It Works
	1.	📄 Upload a medical document – Users upload a PDF, scanned image, or report.
	2.	🔍 OCR Extraction – Google Cloud Vision extracts raw text from the file.
	3.	📚 Knowledge Retrieval – Snowflake retrieves relevant definitions, lab ranges, and glossary terms.
	4.	🤖 AI Processing – Gemini processes the text and outputs structured results:
	•	Plain summary
	•	Key terms and definitions
	•	Actionable steps
	•	Red-flag warnings
	•	Disclaimers
	5.	🌐 Translation & Voice (Optional) – Gemini translates results into another language, and ElevenLabs reads them aloud.
	6.	🖥️ User Display – The frontend displays the results in a clean, accessible, and user-friendly interface.

⸻

📁 Project Structure

clarimed/
│
├── backend/                     # Flask backend
│   ├── app.py                  # Main Flask application (API routes)
│   ├── services/               # Core integrations and AI logic
│   │   ├── gcs.py             # Google Cloud Storage operations
│   │   ├── ocr.py             # Text extraction via Cloud Vision
│   │   ├── gemini.py          # Text generation and translation
│   │   ├── snowflake_client.py# Medical glossary and data retrieval
│   │   ├── elevenlabs.py      # Optional voice synthesis
│   │   └── validate.py        # Output validation and formatting
│   ├── prompts.py             # Prompt templates for Gemini API
│   ├── models.py              # Request/response data schemas
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variable template
│
├── frontend/                   # React.js frontend
│   ├── public/                # Static assets
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── index.js          # Entry point
│   │   ├── components/       # UI components
│   │   │   ├── UploadCard.js       # File upload UI
│   │   │   ├── ResultPane.js       # Summary, glossary, actions
│   │   │   └── LanguageToggle.js   # Language switcher
│   │   ├── api/              # Axios API service
│   │   └── styles/           # Styling and CSS files
│   ├── package.json
│   └── .env.local.example
│
└── README.md                 # Project documentation


⸻

🧑‍💻 Local Development Setup

1. Clone the repository

git clone https://github.com/yourusername/clarimed.git
cd clarimed


⸻

2. Setup Backend (Flask)

cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Fill in your keys and credentials
python app.py

The backend will run on: http://localhost:5000

⸻

3. Setup Frontend (React.js)

cd frontend
npm install
cp .env.local.example .env.local
npm start

The frontend will run on: http://localhost:3000

⸻

🔑 Environment Variables

Backend (.env):

GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp-key.json
GCP_BUCKET_NAME=clarimed-uploads
GEMINI_API_KEY=...
SNOWFLAKE_USER=...
SNOWFLAKE_PASSWORD=...
SNOWFLAKE_ACCOUNT=...
SNOWFLAKE_DATABASE=CLARIMED_DB
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
ELEVENLABS_API_KEY=...

Frontend (.env.local):

REACT_APP_API_BASE=http://localhost:5000


⸻

📊 API Endpoints

Endpoint	Method	Description
/upload-url	GET	Generate a signed URL for GCS file upload
/process	POST	Process an uploaded document and return JSON
/translate	POST	Translate the output into a new language
/tts	POST	Generate audio narration (optional)


⸻

🧠 Example Output

Input: A hospital discharge summary filled with complex medical language.

Output:
	•	Plain Summary: “Your kidneys were under stress due to low hydration.”
	•	Action Items: “Drink more fluids and follow up with your doctor in 7 days.”
	•	Red Flags: “Seek emergency help if you stop urinating or feel faint.”
	•	Glossary:
	•	Creatinine: A chemical waste that indicates kidney function.
	•	Hypovolemia: A low amount of fluid in the bloodstream.

⸻

🏆 Why ClariMed Stands Out
	•	🌍 Social Good – Increases health literacy and access to care.
	•	📚 Education – Helps patients and families understand medical terms.
	•	💡 Entrepreneurial – Real-world product potential for hospitals, clinics, and insurers.
	•	🤖 Best Use of Gemini & Snowflake – Combines state-of-the-art AI with data retrieval.
	•	🎨 Best UI/UX – Clean, accessible, and trustworthy design.

⸻

🧭 Future Roadmap
	•	📱 Mobile app for patients and caregivers
	•	🩺 EHR integration with FHIR/HL7 standards
	•	🔬 Live Q&A chatbot for report clarification
	•	📊 Analytics dashboard for healthcare providers

⸻

⚠️ Disclaimer

ClariMed is an educational tool and not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider with any questions regarding a medical condition.

⸻

👩‍⚕️ About

Built with ❤️ to bridge the gap between complex medical information and human understanding — because everyone deserves to know what their health data means.

⸻
