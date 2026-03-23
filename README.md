# 📊 SmartAlpha AI

An AI-powered stock analysis and trading assistant...

## 🌐 Live Demo

[![Open App](https://img.shields.io/badge/Launch-App-green?style=for-the-badge)](https://smartalpha.streamlit.app/)


## 🚀 Features

* 📈 **Live Stock Data** using Yahoo Finance (yfinance)
* 🤖 **Multi-Agent AI System** (CrewAI)

  * Financial Analyst Agent
  * Strategic Trader Agent
* 🧠 **LLM-powered Insights** for market analysis
* 📊 **Interactive Dashboard** (Streamlit UI)
* 💡 **Trading Recommendations** (Buy / Sell / Hold)
* ⚡ Real-time analysis with clean UI

---

## 🏗️ Tech Stack

* **Python**
* **CrewAI** (Multi-agent orchestration)
* **Streamlit** (Frontend UI)
* **yfinance** (Stock market data)
* **LLMs (Groq / OpenAI)**

---

## 📂 Project Structure

```
CREWAI_MULTI_AGENT/
│
├── app.py              # Streamlit UI
├── main.py             # CLI entry point
├── crew.py             # CrewAI orchestration
│
├── agents/             # AI Agents
├── tasks/              # Task definitions
├── tools/              # Custom tools (stock API)
│
├── .env                # API keys (ignored)
├── requirements.txt
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```
git clone https://github.com/mouktikzz/AI-Financial-Analyst
cd AI-Financial-Analyst
```

### 2️⃣ Create virtual environment

```
python -m venv .venv
.venv\Scripts\activate   # Windows
```

### 3️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 4️⃣ Add environment variables

Create a `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

---

## ▶️ Run the Application

### 🔹 Run Streamlit App

```
streamlit run app.py
```

### 🔹 Run CLI Version

```
python main.py
```

---

## 🧠 How It Works

1. User enters a stock symbol (e.g., AAPL)
2. Tool fetches real-time market data using yfinance
3. **Financial Analyst Agent** analyzes stock performance
4. **Strategic Trader Agent** evaluates risk and suggests action
5. Final output: **Buy / Sell / Hold recommendation**

---

## 📸 Demo

<img width="1807" height="786" alt="image" src="https://github.com/user-attachments/assets/5115be19-1142-4dd4-9224-01074b4a0aa5" />
<img width="1730" height="575" alt="image" src="https://github.com/user-attachments/assets/abd71d54-84b9-41e2-bac9-25fae6953cbb" />
<img width="1690" height="234" alt="image" src="https://github.com/user-attachments/assets/74654c09-0279-4684-bc19-c3e3d5f97bca" />




---

## 💼 Use Case

* Beginner-friendly AI trading assistant
* Demonstrates **GenAI + Multi-Agent Systems**
* Useful for learning financial data analysis

---

## 🔒 Security

* API keys stored in `.env`
* `.env` excluded via `.gitignore`

---

## 🌟 Future Improvements

* 📰 News + Sentiment Analysis Agent
* 📊 Technical Indicators (RSI, Moving Average)
* 🌐 Deployment on Streamlit Cloud
* 📉 Advanced trading strategies

---

## 👨‍💻 Author

**Mouktik Dasari**
AI & Data Enthusiast

---

## ⭐ If you like this project

Give it a ⭐ on GitHub!
