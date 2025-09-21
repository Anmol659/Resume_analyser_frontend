# Innomatics Resume Analyzer - Frontend  

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)  
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-ff4b4b.svg)  
![FastAPI](https://img.shields.io/badge/API-Backend%20(FastAPI)-brightgreen.svg)  

This repository contains the **frontend user interface** for the **Innomatics Resume Analyzer**.  
It’s a web application built with **Streamlit** that provides an intuitive and interactive way for both students and placement teams to use the AI backend.  

The application connects to a separate **FastAPI backend server**, which performs the heavy lifting of document parsing, AI analysis, and database interactions.  

---

## 🖼️ Screenshots  

- **Student Portal View**  
- **Placement Team Dashboard**  

*(Add screenshots here for better visualization)*  

---

## ✨ Features  

- **Dual-Mode Interface**: Separate, tailored views for *Students* (to check their own resume) and *Placement Teams* (to batch-analyze multiple candidates).  
- **Easy File Uploads**: Simple drag-and-drop interface for job descriptions and multiple resumes.  
- **Interactive Results**: Visualizes analysis with dynamic progress gauges, styled verdicts, and detailed, structured feedback from the AI.  
- **Candidate Ranking**: Provides a sortable and filterable dashboard for recruiters to easily rank candidates by relevance score.  
- **Detailed Breakdowns**: Expandable sections to view AI-generated summaries, strengths, areas for improvement, and skills gaps for each candidate.  

---

## 🛠️ Tech Stack  

- **Framework**: Streamlit  
- **Language**: Python  
- **API Client**: `requests`  
- **Data Display**: `pandas`  

---

## 🚀 Getting Started  

### 1. Prerequisites  
- Python 3.10 or higher  
- Backend server must be running and accessible via a URL  

### 2. Installation & Setup  

a. Clone the repository:  
```bash
git clone <your-frontend-repository-url>
cd <frontend-repository-folder>
