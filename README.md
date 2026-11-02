# 🏥 WARD360 AI – Intelligent Home Healthcare Monitoring System
# WARD360 AI --- Complete Setup & Run Guide(line=756)only how to run this project.

### Your Home. Your Health. One Intelligent Ward.

**Hackathon:** Operation Ward Zero  
**Theme:** Build a Hospital That Fits Inside a Bedroom  
**Project Category:** IoT | Full Stack Development | Artificial Intelligence | Machine Learning

---

## 1. Project Overview

WARD360 AI is an intelligent home healthcare monitoring and early-warning platform designed to transform an ordinary bedroom into a smart healthcare monitoring environment.

Hospitals use continuous patient monitoring systems, healthcare professionals and alert mechanisms to identify changes in patient conditions. At home, however, patients often depend on family members and caregivers who may not have access to continuous monitoring or early-warning systems.

WARD360 AI addresses this challenge by integrating simulated IoT sensors, a full-stack monitoring dashboard and AI/ML-based analysis.

The system collects patient vital signs, analyses health patterns, identifies unusual measurements, estimates possible future trends and generates alerts to help caregivers respond appropriately.

Our central workflow is:

**SENSE → UNDERSTAND → PREDICT → ALERT → RESPOND**

All patient information used in this prototype is synthetic or simulated. The system is an experimental healthcare decision-support demonstration, not a clinically validated medical device.

---

## 2. Problem Statement

**Build an Intelligent Home Healthcare Monitoring and Response System.**

Develop a software-based healthcare monitoring solution that demonstrates how a patient's home can operate like a small intelligent hospital ward.

The system should demonstrate:

- Continuous patient vital monitoring.
- Simulated IoT sensor data collection.
- AI-based anomaly and risk identification.
- Historical health trend analysis.
- Experimental 24–48-hour forecasting.
- Caregiver notification and acknowledgement.
- System reliability during connectivity interruptions.
- Explainable observations and responsible healthcare information handling.

---

## 3. Proposed Solution

WARD360 AI provides a unified platform consisting of five major stages.

### Stage 1: Sense

Collect and simulate patient health measurements through software-based IoT devices.

### Stage 2: Understand

Process incoming measurements and compare them with historical readings and patient-specific baselines.

### Stage 3: Predict

Analyse historical trends and generate experimental future estimates for selected health parameters over 24 and 48 hours.

### Stage 4: Alert

Generate explainable alerts when configured demonstration conditions identify measurements or patterns requiring caregiver review.

### Stage 5: Respond

Allow caregivers to review alerts, acknowledge them and track response activity.

---

## 4. Key Features

### 4.1 Patient Monitoring

Monitor multiple simulated patient health parameters:

| Parameter | Unit |
|---|---|
| Heart Rate | BPM |
| Body Temperature | °C |
| Oxygen Saturation | SpO₂ (%) |
| Blood Pressure | mmHg |
| Respiratory Rate | Breaths/min |
| Movement / Activity | Activity data |

The dashboard provides patient readings, measurement history and visualisations.

### 4.2 IoT Sensor Simulation

Physical hardware is not mandatory.

WARD360 AI uses software-based sensor simulation to demonstrate how connected monitoring devices can transmit patient readings to the backend.

Features include:

- Simulated bedside monitoring devices.
- Automatic measurement generation.
- HTTP-based sensor communication.
- Multiple sensor scenarios.
- Sensor disconnection demonstration.
- Delayed data transmission handling.

### 4.3 AI-Based Anomaly Detection

The system analyses patient measurements to identify unusual patterns.

The analysis can consider:

- Current measurements.
- Historical patient readings.
- Personal baseline comparisons.
- Unusual increases or decreases.
- Multiple health parameters.

The objective is to identify observations that may require caregiver attention.

### 4.4 Explainable Risk Assessment

Rather than displaying only a risk label, the platform provides explanations for generated observations.

Examples:

- Heart rate has increased compared with recent readings.
- Temperature has changed significantly from the recent baseline.
- Oxygen saturation is outside a configured demonstration range.
- Multiple unusual measurements have been detected.

Risk categories and thresholds are experimental software rules, not clinical classifications.

### 4.5 Predictive Trend Analysis

WARD360 AI includes experimental trend forecasting.

The system analyses historical measurements and estimates possible future trends.

Forecasting parameters include:

- Heart rate.
- Body temperature.
- SpO₂.
- Systolic blood pressure.
- Diastolic blood pressure.
- Respiratory rate.

Forecasting horizons:

| Horizon | Description |
|---|---|
| 24 hours | Experimental estimate for the next day |
| 48 hours | Experimental estimate for the next two days |

The dashboard can display historical readings, estimated future values, trend direction and prediction uncertainty where supported by the forecasting implementation.

These estimates are not clinically validated deterioration predictions.

### 4.6 Alert and Escalation Management

The alert management module supports:

- Alert generation.
- Alert severity categorisation.
- Explanation of detected observations.
- Caregiver acknowledgement.
- Response tracking.
- Alert history.

Additional escalation mechanisms can be integrated in future versions.

### 4.7 Caregiver Management

The platform is designed to support different healthcare user roles.

- Administrator.
- Caregiver.
- Doctor.

The intended workflows include patient monitoring, alert review and caregiver coordination.

### 4.8 Reliability and Resilience

The system demonstrates how a monitoring platform can respond to temporary technical failures.

Reliability scenarios include:

- Network interruption.
- Delayed data transmission.
- Duplicate event detection.
- Sensor disconnection.
- Local data buffering.
- Data synchronisation after reconnection.

The goal is to demonstrate reliable data handling even when connectivity is temporarily unavailable.

### 4.9 Additional Advanced Modules

The extended project design also includes:

- Experimental fall detection.
- Emergency text and voice assistant.
- Digital patient twin.
- Daily and weekly healthcare reports.
- Caregiver attendance monitoring.
- Audit logging.
- Role-based access control.

**Implementation note:** These extended capabilities should only be presented as completed functionality when their corresponding modules are implemented and tested in the current repository.

---

## 5. Technology Stack

### Frontend
- React.js
- JavaScript
- Vite
- HTML5
- CSS3
- Recharts

### Backend
- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- REST APIs

### Database
- SQLite

### Artificial Intelligence and Machine Learning
- NumPy
- Scikit-learn
- Statistical analysis
- Anomaly detection
- Trend forecasting
- Explainable risk assessment

### IoT
- Python-based sensor simulator
- HTTP communication
- Synthetic sensor measurements

### Development Tools
- Visual Studio Code
- Git
- GitHub
- Postman (optional)
- Swagger UI

---

## 6. System Architecture

```text
             PATIENT / SIMULATED SENSORS
                        |
                        v
              IoT SENSOR SIMULATOR
                        |
                        v
                FASTAPI BACKEND
                        |
              DATA VALIDATION
                        |
                        v
                  DATABASE
                        |
             HISTORICAL READINGS
                        |
                        v
                 AI / ML ENGINE
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
      ANOMALY       RISK          TREND
      DETECTION   ASSESSMENT    FORECASTING
          |             |             |
          +-------------+-------------+
                        |
                        v
                 ALERT ENGINE
                        |
                        v
              CAREGIVER RESPONSE
                        |
                        v
                REACT DASHBOARD
```

---

## 7. Project Folder Structure

```text
WARD360-AI/
│
├── backend/
│   ├── app/
│   ├── ml/
│   │   ├── risk.py
│   │   └── trend.py
│   │
│   ├── seed.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── ward360.db
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── iot/
│   └── simulator.py
│
├── ml/
│
├── tests/
│   ├── conftest.py
│   └── test_workflow.py
│
├── data/
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEMO_SCRIPT.md
│   ├── DEPLOYMENT.md
│   └── SUBMISSION_KIT.md
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── pytest.ini
└── README.md
```

---

## 8. System Requirements

Install the following software before running the project.

| Software | Minimum requirement |
|---|---|
| Python | 3.11+ |
| Node.js | 20+ |
| npm | Included with Node.js |
| VS Code | Latest stable version |
| Git | Optional |
| Docker Desktop | Not required for local execution |

The project can run directly on Windows without Docker.

### Download links

- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/en/download
- VS Code: https://code.visualstudio.com/
- Git: https://git-scm.com/downloads

---

## 9. Installation and Setup

Follow these instructions to run WARD360 AI locally on Windows.

### Step 1: Clone or download the project

If using Git:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Alternatively, download and extract the project ZIP.

Open the extracted WARD360-AI folder in VS Code.

### Step 2: Verify installations

Open the VS Code terminal.

```powershell
python --version
```

```powershell
node --version
```

```powershell
npm --version
```

Make sure Python and Node.js meet the minimum requirements.

### Step 3: Configure the backend

Open the first terminal.

```powershell
cd backend
```

Create a Python virtual environment:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then activate the environment again.

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install backend dependencies:

```powershell
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Check the `.env.example` file.

Create a `.env` file based on the example and configure the required values.

Never upload secret keys, production passwords or sensitive configuration to GitHub.

### Step 5: Initialise the database

Run:

```powershell
python seed.py
```

This initialises the sample database and demo data according to the seed script.

### Step 6: Start the backend

Run:

```powershell
python -m uvicorn app.main:app --reload
```

Backend address:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

Keep this terminal running.

### Step 7: Install frontend dependencies

Open a second terminal in VS Code.

```powershell
cd frontend
```

Install packages:

```powershell
npm install
```

### Step 8: Start the frontend

```powershell
npm run dev
```

Open:

http://localhost:5173

The WARD360 AI dashboard should now load.

### Step 9: Run the IoT simulator

Open a third terminal.

```powershell
cd iot
```

Run:

```powershell
python simulator.py --device 1 --scenario hypoxia
```

The simulator demonstrates sensor communication using synthetic readings.

### Step 10: Run automated tests

Open another terminal at the project root.

```powershell
cd backend
```

Install development dependencies:

```powershell
pip install -r requirements-dev.txt
```

Return to the root folder:

```powershell
cd ..
```

Run tests:

```powershell
python -m pytest
```

---

## 10. Demo Login Accounts

The local demo environment provides the following sample accounts, as configured in the project.

| Role | Email | Password |
|---|---|---|
| Administrator | admin@ward360.test | Admin@123 |
| Caregiver | caregiver@ward360.test | Care@123 |
| Doctor | doctor@ward360.test | Doctor@123 |

These credentials are for local demonstration only.

---

## 11. API Documentation

WARD360 AI uses REST APIs for communication between the frontend, backend and simulated devices.

The FastAPI Swagger interface provides interactive API documentation.

Open:

http://localhost:8000/docs

Available API groups depend on the implemented backend routes and may include:

- Authentication.
- Patient management.
- Patient readings.
- Monitoring.
- AI analysis.
- Alerts.
- Caregiver management.
- Reports.

Swagger UI can be used to inspect requests, responses and available endpoints.

---

## 12. Testing and Demonstration Scenarios

The prototype can demonstrate the following scenarios using synthetic data.

| Scenario | Expected demonstration |
|---|---|
| Normal readings | Display simulated patient measurements |
| Unusual heart rate | Identify a configured unusual measurement |
| Temperature variation | Analyse a temperature change |
| Low SpO₂ | Generate an observation for review |
| Rising trend | Demonstrate experimental forecasting |
| Network interruption | Demonstrate offline handling |
| Delayed transmission | Identify delayed measurements |
| Duplicate event | Demonstrate duplicate protection |
| Sensor disconnection | Demonstrate device status handling |
| Caregiver acknowledgement | Record alert acknowledgement |

Actual results depend on the implemented modules and configured demonstration scenarios.

---

## 13. Evaluation Criteria Alignment

WARD360 AI is designed around the published Operation Ward Zero evaluation criteria.

| Evaluation criterion | Project contribution |
|---|---|
| End-to-End Integration (25%) | IoT simulation, backend, AI/ML and frontend integration |
| Technical Skills (20%) | Python, FastAPI, React, database and ML |
| Reliability & Resilience (20%) | Data validation, duplicate handling and offline buffering |
| Practical Implementation (20%) | Home healthcare dashboard and caregiver workflow |
| Explainability & Clinical Safety (15%) | Explainable observations, synthetic data and limitations |

---

## 14. Privacy and Clinical Safety

WARD360 AI is an experimental technology prototype.

Important safety considerations:

- All demonstration patient data should be synthetic.
- Do not upload real patient information without appropriate authorisation.
- The system does not provide medical diagnosis.
- Experimental forecasts are not clinically validated.
- Demonstration thresholds must not be treated as medical advice.
- Alerts are intended to demonstrate caregiver communication workflows.
- The prototype must not replace healthcare professionals or emergency services.

---

## 15. Current Limitations

The prototype has several limitations:

1. Synthetic sensor readings are used instead of real medical device measurements.
2. Forecasting is experimental and requires appropriate datasets and validation.
3. Demonstration anomaly thresholds are not clinically validated.
4. Internet connectivity and device reliability are simulated.
5. Production-grade healthcare security and privacy compliance require further development.
6. Actual emergency notification integrations require additional implementation and testing.

---

## 16. Future Improvements

Potential future development includes:

- Physical ESP32 and IoT sensor integration.
- MQTT-based communication.
- Secure caregiver and doctor authentication.
- Improved multi-parameter predictive modelling.
- Clinically validated forecasting datasets.
- Advanced patient digital twin.
- More robust fall detection.
- Voice-based caregiver assistant.
- Real-time SMS and notification integration.
- Advanced caregiver attendance tracking.
- Production-grade audit logging.
- Cloud deployment and scalable database infrastructure.

---

## 17. Hackathon Deliverables

The Operation Ward Zero submission requires:

**A. Working Prototype**
- Functional home healthcare monitoring dashboard.
- Simulated patient data collection.
- Risk assessment.
- Alert generation.
- Caregiver acknowledgement.

**B. Source Code Repository**
- GitHub or GitLab repository.
- Source code.
- README.
- Installation instructions.
- Dependencies.
- Synthetic sample data.

**C. Technical Documentation**
- Problem understanding.
- System architecture.
- Technology stack.
- Data processing.
- Risk assessment.
- Assumptions and limitations.

**D. Demonstration Video**
- Approximately three minutes.
- Sensor simulation.
- Platform monitoring.
- AI risk detection.
- Alert generation.
- Caregiver response.

---

## 18. Three-Minute Demonstration Flow

| Time | Demonstration |
|---|---|
| 0:00–0:25 | Introduce the problem and WARD360 AI |
| 0:25–0:55 | Show simulated patient vital signs |
| 0:55–1:25 | Demonstrate AI anomaly detection |
| 1:25–1:55 | Show experimental 24–48-hour forecasting |
| 1:55–2:25 | Demonstrate alerts and reliability scenarios |
| 2:25–2:50 | Show caregiver acknowledgement |
| 2:50–3:00 | Explain the impact and future improvements |

---

## 19. Project Impact

WARD360 AI demonstrates how software-based IoT monitoring, full-stack development and artificial intelligence can work together to support home healthcare.

By bringing monitoring, explainable observations, experimental trend analysis and caregiver response into one platform, the project explores a more connected and responsive home healthcare environment.

**Our vision: Make every bedroom a smarter and safer place for healthcare monitoring.**

---

## 20. Team and Acknowledgements

**Project:** WARD360 AI  
**Hackathon:** Operation Ward Zero  
**Challenge Organiser:** Wooble Software Private Limited

Developed as a hackathon prototype using software simulation, synthetic patient data, open-source technologies and AI-assisted development tools.

---

### Final Note

WARD360 AI is an educational and experimental prototype. It is not a medical device and must not be used for clinical diagnosis, treatment decisions or emergency response.

**SENSE → UNDERSTAND → PREDICT → ALERT → RESPOND**

**WARD360 AI — Your Home. Your Health. One Intelligent Ward.**





# WARD360 AI --- Complete Setup & Run Guide

**Your Home. Your Health. One Intelligent Ward.**

This guide covers the local Windows + VS Code setup.

> **Safety:** This is a hackathon prototype using synthetic/simulated
> patient data. It is not a medical device and must not be used for
> diagnosis, treatment, or emergency decisions.

## 1. Install these tools first

  Tool                         Required      Purpose
  ---------------------------- ------------- ---------------------------------
  Python 3.11+                 Yes           FastAPI backend and AI/ML
  Node.js 20+ (includes npm)   Yes           React/Vite frontend
  VS Code                      Recommended   Code editor
  Git                          Optional      GitHub/version control
  Docker Desktop               No            Not needed for this local setup

Downloads: - Python: https://www.python.org/downloads/ - Node.js:
https://nodejs.org/ - VS Code: https://code.visualstudio.com/ - Git:
https://git-scm.com/downloads

On Windows, enable **Add Python to PATH** during installation if
offered. After installing, restart VS Code and check:

``` powershell
py --version
python --version
node --version
npm --version
```

## 2. Open the project

1.  Extract the ZIP.
2.  In VS Code choose **File → Open Folder**.
3.  Open the main `WARD360-AI` folder, containing `backend`, `frontend`,
    `iot`, `docs`, and `README.md`.
4.  Open **Terminal → New Terminal**.

## 3. Backend setup --- Terminal 1

``` powershell
cd backend
py -m venv .venv
```

Activate the environment:

``` powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

``` powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

The prompt should show `(.venv)`. Install dependencies:

``` powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If `backend/seed.py` exists, initialise demo data:

``` powershell
python seed.py
```

Start the backend:

``` powershell
python -m uvicorn app.main:app --reload
```

Keep this terminal open. Expected output includes:

``` text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

Open API documentation: http://127.0.0.1:8000/docs

The root URL `http://127.0.0.1:8000/` may show `{"detail":"Not Found"}`
if no homepage route is defined. That alone does not mean the backend
failed.

## 4. Frontend setup --- Terminal 2

Do not stop the backend. Open a second VS Code terminal. From the
project root:

``` powershell
cd frontend
npm install
npm run dev
```

Open the exact local URL Vite prints, usually http://localhost:5173/.

The previously supplied project README lists these demo accounts:

  Role        Email                    Password
  ----------- ------------------------ ------------
  Admin       admin@ward360.test       Admin@123
  Caregiver   caregiver@ward360.test   Care@123
  Doctor      doctor@ward360.test      Doctor@123

These are demo credentials only. If they do not work, check the current
`backend/seed.py` and authentication configuration; do not assume they
were seeded.

## 5. Optional IoT simulator --- Terminal 3

The dashboard may have a built-in simulator; try that first. For the
separate simulator, from the project root:

``` powershell
cd iot
```

If `iot/requirements.txt` exists:

``` powershell
python -m pip install -r requirements.txt
```

The supplied project instructions mention:

``` powershell
python simulator.py --device 1 --scenario hypoxia
```

Run it only if `iot/simulator.py` exists. Check supported options with:

``` powershell
python simulator.py --help
```

Use the actual filename and options present in your project if they
differ.

## 6. Run tests --- optional

With the backend virtual environment active, from the project root:

``` powershell
python -m pytest
```

If `backend/requirements-dev.txt` exists and test packages are missing:

``` powershell
cd backend
python -m pip install -r requirements-dev.txt
cd ..
python -m pytest
```

## 7. Daily startup after initial installation

You normally do not need to reinstall packages every time.

**Terminal 1 --- Backend:**

``` powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

**Terminal 2 --- Frontend:**

``` powershell
cd frontend
npm run dev
```

**Terminal 3 --- Optional simulator:**

``` powershell
cd iot
python simulator.py --device 1 --scenario hypoxia
```

Open the frontend URL printed by Vite.

## 8. Common errors

**`uvicorn` is not recognized**

Activate the backend `.venv`, then run:

``` powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

**`npm` is not recognized**

Install Node.js LTS, restart VS Code, then check `node --version` and
`npm --version`.

**PowerShell blocks activation**

``` powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

**Port 8000 is already in use**

Stop the old backend with `Ctrl+C` in its terminal before starting
another one.

**Port 5173 is busy**

Vite may print an alternative port such as 5174. Open the exact URL it
prints. The backend CORS configuration allows both the default 5173 port
and Vite's 5174 fallback port.

**Frontend cannot connect to backend**

Confirm the backend is running, `/docs` opens, the frontend API base URL
points to the correct backend, and CORS permits the frontend origin. If
you changed backend CORS settings, restart the backend to apply them.
Check the browser console and backend terminal for errors.

**Demo login or database is missing**

If `backend/seed.py` exists, run it from inside `backend` with `.venv`
active:

``` powershell
python seed.py
```

## 9. Environment and security

-   Check `.env.example` in the project root and/or `backend`. Create
    `.env` only if the application requires it.
-   Use only required configuration values. Never publish passwords, API
    keys, JWT secrets, or `.env`.
-   Do not put real patient information into this prototype.
-   Do not describe experimental forecasts as clinically validated
    predictions.
-   Keep local database files and secrets out of public GitHub
    repositories.
-   Docker Desktop is not required for this local Windows setup.

## 10. Final checklist

-   [ ] Python 3.11+ installed
-   [ ] Node.js 20+ and npm installed
-   [ ] Main project folder opened in VS Code
-   [ ] Backend virtual environment activated
-   [ ] Backend requirements installed
-   [ ] Demo database seeded if `seed.py` exists
-   [ ] Backend running on port 8000
-   [ ] Swagger docs open at `/docs`
-   [ ] Frontend packages installed
-   [ ] Frontend running at Vite URL
-   [ ] Dashboard opens
-   [ ] Synthetic simulator tested if included
-   [ ] Tests run and reviewed

**WARD360 AI --- Sense → Understand → Predict → Alert → Respond**
