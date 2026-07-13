# 🏆 Lakehouse: Futebol Brasileiro - Série A

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/framework-Dash-orange.svg)](https://dash.plotly.com/)
[![Kubernetes](https://img.shields.io/badge/orchestration-Kubernetes-blue.svg)](https://kubernetes.io/)
[![Airflow](https://img.shields.io/badge/orchestration-Apache_Airflow-red.svg)](https://airflow.apache.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Overview

This project is a high-performance, end-to-end **Data Lakehouse** platform designed to ingest, process, and visualize complex datasets from the Brazilian Football Championship (Série A). 

Moving beyond traditional data warehousing, this architecture implements a modern **Medallion Architecture** (Bronze, Silver, Gold), ensuring data quality, lineage, and high-speed analytical capabilities. The platform integrates **Artificial Intelligence** for automated insights and follows strict **Production-Grade** standards for security, observability, and DevOps.

---

## 🏗️ Architecture

<img src="https://i.ibb.co/fGDyBVVS/architecture.png" alt="System Architecture" width="100%">

The data flows through a structured pipeline to ensure maximum reliability:

* **🥉 Bronze (Raw):** Ingests raw data from multiple sources in its original format, preserving the full history.
* **🥈 Silver (Cleansed):** Data is cleaned, normalized, and validated. Schema enforcement and type recovery agents ensure consistency.
* **🥇 Gold (Curated):** Highly optimized, business-ready datasets stored in **Apache Parquet** format, specifically modeled for high-speed analytical queries and dashboard consumption.

---

## ✨ Key Engineering Features

### 🧠 AI & Intelligent Insights
* **LLM Integration:** Powered by OpenAI and Ollama providers to generate semantic insights directly from the data.
* **Semantic Guardrails:** Implements advanced guardrails to ensure AI responses are contextually accurate and safe.
* **Automated Schema Recovery:** Intelligent agents that detect and fix data type discrepancies during the pipeline execution.

### 🛡️ Security & Governance (Enterprise Grade)
* **Identity & Access:** Kubernetes-native **RBAC (Role-Based Access Control)** for secure resource management.
* **Data Protection:** Implementation of **Fernet Encryption** for sensitive credentials and configuration.
* **PII & Content Guardrails:** Automated scanning and semantic checks to prevent exposure of Personally Identifiable Information (PII).
* **Secure CI/CD:** Integrated secret detection in pre-commit hooks to prevent credential leakage.

### 📈 Observability & Reliability
* **Full-Stack Monitoring:** Integrated with **Prometheus** and **OpenTelemetry** for real-time metrics and distributed tracing.
* **Structured Logging:** High-fidelity logging using `structlog` and `colorlog` for efficient debugging and audit trails.
* **Automated Orchestration:** Production-ready **Apache Airflow** DAGs managed via Kubernetes, ensuring scalable and resilient task execution.

### 📊 Advanced Analytics Dashboard
* **Real-time Interaction:** A high-performance web application built with **Dash (Plotly)** and **Flask**.
* **Dynamic Filtering:** Multi-dimensional filtering (Time, Year, Month, Page) with optimized state management using `dcc.Store`.
* **Responsive UI:** Custom-designed components including interactive sidebars, bottom sheets, and specialized data visualizations.

---

## 🛠️ Tech Stack

| Category | Technologies |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Data Engineering** | Pandas, Apache Parquet, Apache Airflow |
| **Architecture** | Data Lakehouse (Medallion Pattern) |
| **Orchestration** | Kubernetes (K8s), Docker |
| **Observability** | Prometheus, OpenTelemetry, Structlog |
| **AI / LLM** | OpenAI API, Ollama, Semantic Guardrails |
| **Frontend/BI** | Dash (Plotly), Flask, CSS3 |
| **CI/CD & DevOps** | GitHub Actions, Pre-commit, Kubectl |

---

## ⚙️ Getting Started

### Prerequisites
* Docker & Kubernetes Cluster (Minikube/Kind/Cloud)
* Python 3.10+
* Airflow (managed via K8s)

### Installation & Deployment
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Romilsonlonan/football-brazil-data-engineering.git
   cd football-brazil-data-engineering
   ```

2. **Setup Environment:**
   ```bash
   # Generate and configure encryption keys
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

3. **Deploy Infrastructure:**
   ```bash
   ./start-services.sh
   ```

4. **Run Pipelines:**
   Access the Airflow UI to trigger the Bronze $\to$ Silver $\to$ Gold DAGs.

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.

---
<p align="center">Built with ❤️ by [Romilson](https://github.com/Romilsonlonan)</p>
