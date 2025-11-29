# 📄 AI Job Recommendation System

### Get personalized job recommendations from LinkedIn & Naukri based on your resume using AI.

---

## 📝 **Project Overview**

This project allows users to upload a **PDF resume**, extracts text from it, and uses **AI (OpenRouter)** to:

* Summarize the resume
* Identify missing skills & gaps
* Generate a future career roadmap
* Extract relevant job titles/keywords
* Fetch real-time job listings from **LinkedIn** and **Naukri.com**
* Display job recommendations inside a Streamlit web app

This makes it a **complete AI-powered career assistant**.

---

## 🚀 **Features**

### 🔹 1. Resume Processing

* PDF text extraction with PyMuPDF
* AI-generated summary
* Skill gap analysis
* Personalized future roadmap

### 🔹 2. Smart Job Search

* Extracts job titles & keywords using AI
* Fetches jobs from LinkedIn (via Apify)
* Fetches jobs from Naukri.com (via Apify)
* Displays company name, role, location, apply links

### 🔹 3. Clean & Interactive UI

* Built using Streamlit
* Upload, analyze, and get job recommendations instantly

### 🔹 4. API Integrations

* OpenRouter AI API
* Apify LinkedIn Scraper
* Apify Naukri Job Scraper

---

## 🖥️ **Demo Screenshot**

(Add your screenshot here)

```
![App Screenshot](./screenshot.png)
```

---

## 🧰 **Tech Stack**

| Technology         | Purpose                             |
| ------------------ | ----------------------------------- |
| **Python**         | Backend logic                       |
| **Streamlit**      | UI framework                        |
| **PyMuPDF (fitz)** | PDF text extraction                 |
| **OpenRouter API** | AI summarization & processing       |
| **Apify Platform** | Job scraping from LinkedIn & Naukri |
| **dotenv**         | Environment variable management     |
| **Requests**       | API calls                           |

---

## 📦 **How to Use**

### 🔧 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-job-recommendation-system.git
cd ai-job-recommendation-system
```

### 📥 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 🔑 3. Add API Keys

Create a **.env** file in the root folder:

```
OPENROUTER_API_KEY=your_openrouter_api_key
APIFY_API_KEY=your_apify_api_key
```

### ▶️ 4. Run the Streamlit App

```bash
streamlit run app.py
```

### 🧪 5. Use the App

* Upload your **PDF resume**
* View resume summary, skill gaps, and roadmap
* Click **Get Job Recommendations**
* Browse LinkedIn + Naukri jobs

---

## 🤝 **How to Contribute**

We welcome all contributions!

### 1. Fork the repository

### 2. Create a new feature branch

```bash
git checkout -b feature-name
```

### 3. Commit your changes

```bash
git commit -m "Added new feature"
```

### 4. Push & Submit PR

```bash
git push origin feature-name
```

---

## 👤 **Author**

**Abdul Rehman**
AI Student | Data Science Enthusiast


