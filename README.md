
# 🚀 AI Powered Lead Management

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Platform](https://img.shields.io/badge/platform-web-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)]()
[![React](https://img.shields.io/badge/react-18+-61DAFB.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

**Supercharge your sales workflow with intelligent automation.**  
*Instant Reply Scoring • Smart Next Actions • Auto-Drafted Responses • Seamless Attachments*

[Request Demo](https://example.com) • [Report Bug](https://example.com) • [Request Feature](https://example.com)

</div>

---

## 🌟 Overview

**AI Powered Lead Management** is a cutting-edge CRM extension designed to eliminate the busywork from sales. By leveraging **OpenRouter AI (GPT-4o)** and **Google Gemini**, it automatically analyzes inbound leads, prioritizes your inbox, and drafts professional responses in seconds.

Stop guessing which leads are hot. Stop manually typing the same "standard pricing" email. Let AI handle the boring stuff so you can focus on **closing deals**.

## ✨ Key Features

### 🧠 Intelligent Lead Scoring
Never waste time on cold leads again.
- **Sentiment Analysis**: Detects if a lead is `INTERESTED`, `ASKING_PRICE`, `MEETING_READY`, or `NOT_INTERESTED`.
- **Priority Scoring (0-100)**: Automatically ranks emails so you answer the most important ones first.
- **Visual Indicators**: Color-coded badges (High, Medium, Low) make your inbox scanable at a glance.

### 🤖 AI Next Best Action
Your personal sales strategist.
- **Action Plans**: Suggests 3 concrete steps for every reply (e.g., "Schedule Call", "Send Pricing PDF").
- **Urgency Detection**: Tells you if you need to act `NOW`, `TODAY`, or `THIS_WEEK`.
- **Context Aware**: Remembers the lead's name, company, and previous context.

### ✍️ Auto-Draft Replies
Draft emails in milliseconds, not minutes.
- **One-Click Generation**: Creates full email drafts based on the lead's intent.
- **Tone Selector**: Choose between `FRIENDLY`, `FORMAL`, or `SHORT` styles.
- **Smart Placeholders**: Automatically inserts meeting links and attachment references.

### 📎 Seamless Attachments & Threading
- **Integrated Uploads**: Drag-and-drop files directly in the reply editor.
- **Supabase Storage**: Secure, scalable file hosting.
- **Perfect Threading**: Emails appear correctly nested in Gmail/Outlook threads.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI Engine**: OpenRouter (GPT-4o) / Google Gemini (Fallback)
- **Database**: Supabase (PostgreSQL)
- **Email**: SMTP/IMAP with threading support

### Frontend
- **Framework**: React (Vite)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **State**: React Query / Local State

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 16+
- Supabase Account

### 1. Clone & Setup Backend
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in `backend/`:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENROUTER_API_KEY=your_openrouter_key
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
```

### 3. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Run Application
Start the backend server:
```bash
# In backend/
python main.py
```
Visit `http://localhost:3000` to see your dashboard!

---

## 📸 Screenshots

<div align="center">
  <img src="https://via.placeholder.com/800x400?text=Dashboard+Preview" alt="Dashboard" style="border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;">
  <br>
  <em>Smart Inbox with AI Scoring</em>
</div>

<div align="center">
<br>
  <img src="https://via.placeholder.com/800x400?text=AI+Draft+Editor" alt="Editor" style="border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
  <br>
  <em>Auto-Drafting & Attachments</em>
</div>

---

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---


<div align="center">
  <p>Built with ❤️ by Ayush Gajera</p>
</div>
