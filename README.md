#  AI-Powered Data Assistant

This Streamlit-based app lets you upload CSV/Excel datasets and ask questions using natural language. It uses an AI agent (LangChain + OpenAI) to analyze your data, generate Python code, and present interactive outputs. It also automates EDA reporting and supports user authentication.

---

##  Features

- Upload any tabular dataset (CSV/Excel)
- Ask questions like `"Top 5 countries by sales"` or `"Plot revenue by month"`
- Visual output: charts, tables, KPIs
- Auto-generated EDA report with `sweetviz` 
- Chat memory using LangChain's `ConversationBufferMemory`
- Secure login with `streamlit-authenticator`
- Daily email summary automation (via SMTP )
- Deployable via Streamlit Cloud + GitHub Actions

---

##  Tech Stack

- **Python**
- **Pandas**, **LangChain**, **OpenAI API**
- **Streamlit** (UI)
- **streamlit-authenticator** (login)
- **Docker** (optional for containerization)
- **GitHub Actions** (CI/CD)
- **sweetviz** or **ydata-profiling** (EDA automation)

---
