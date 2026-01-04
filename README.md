# GFGBQ-Team-axiom-forage


## 1. Problem Statement
Hospitals face significant challenges in managing resources during unexpected surges in patient volume, often driven by external factors like weather events, seasonal illnesses, and public festivals. These surges can lead to shortages in critical resources such as oxygen, medicine, and staff, as well as overcrowding in ICU and ER departments. The lack of predictive insights makes it difficult for hospital administrators to proactively allocate resources and mitigate risks.

This project aims to solve this by deploying an AI-driven predictive model that analyzes internal hospital data (occupancy, inventory) and external environmental factors to forecast stress levels, risk scores, and potential increases in patient influx. This enables proactive decision-making to ensure optimal patient care and operational efficiency.

## 2. Project Name
**Axiom Forage**


## 3. Team Name
**GFGBQ-Team-axiom-forage**
Members:
1.Jaya Sri Vardhan Samgoju (Team Lead)
2.Yaswanth Krishna Jonnalagadda
3.K.Manikanta Vasu
4.Teja Matta

## 4. Deployed Link
(Optional)

## 5. Demonstration Video
[Link to 3-minute video placeholder]
https://drive.google.com/file/d/1WPJtIrb5EeRn_3XMFFiwF6ENoo79Ec-c/view?usp=drivesdk

## 6. Presentation
https://docs.google.com/presentation/d/1rY67HnaZeJCKZ4R2bS3_CSN1qIZ30k9C/edit?usp=drivesdk&ouid=116628029549493605793&rtpof=true&sd=true

# Project Overview
**Axiom Forage** is a comprehensive predictive modeling solution designed to help hospitals anticipate resource shortages and patient surges. By leveraging historical hospital data and external environmental factors (weather, festivals, etc.), the system provides actionable insights to optimize ICU and ER allocation, ensuring better patient outcomes and operational resilience.

# Setup and Installation

### Prerequisites

- **Python 3.9+**
- **Node.js & npm**

### Backend Setup
1. Navigate to the project directory:
   ```bash
   cd GFGBQ-Team-axiom-forage
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the backend server:
   ```bash
   # The application runs on port 8001 to avoid common port conflicts
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8001 --reload
   ```
   The API will be available at `http://localhost:8001`.

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The application will be accessible at `http://localhost:3000`.

# Usage
1. Ensure both the **Backend** (Port 8001) and **Frontend** (Port 3000) servers are running.
2. Open your web browser and navigate to `http://localhost:3000`.
3. Use the **Dashboard** to view real-time risk metrics, predicted patient surges, and resource recommendations.
4. (Optional) Use the **Simulation** mode (if available) to test how different weather or seasonal factors might affect hospital stress levels.

# Screenshots
*(Placeholders for future screenshots)*
Landing page : https://drive.google.com/file/d/1W7VKAV1hCQZ8W7uF9JUU_B1jfkcDmJ5n/view?usp=sharing

Dashboard : https://drive.google.com/file/d/1wqM4GxbmWhEyR2MAMOf8naK457V0fL1y/view?usp=sharing

![Risk Analysis](placeholder-image-url) : https://drive.google.com/file/d/1ID8oQBtEwKvOj-l5vr59oZiCjW6KJ095/view?usp=sharing
