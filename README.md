# AI-Powered Doctor Appointment Booking Assistant

An intelligent conversational chatbot that allows users to book doctor appointments through natural language chat. The system detects booking intent, collects details through multi-turn conversations, validates inputs, stores bookings in a database, and provides an admin dashboard for booking management.

## Key Features

### User Chat Interface
- Natural language chat interface
- Intelligent booking intent detection
- Multi-step conversational slot filling
- Real-time input validation (email, phone, date, time)
- Booking summary and confirmation
- Automatic booking ID generation

### Admin Dashboard
- View all bookings in a table
- Customer and booking details
- Date & time information
- Booking status tracking
- Timestamp records
- Email Confirmation
---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **LLM** | Groq (LLaMA 3.1 – 8B Instant) |
| **LLM Framework** | LangChain |
| **Backend** | Python |
| **Database** | SQLite |
| **Email** | Brevo |
| **Validation** | Regex + datetime |

---

## 📂 Project Structure

```
ChatBot/
│
├── app/
│   ├── __init__.py
│   └── main.py                 # Main Streamlit application
│
├── models/
│   ├── __init__.py
│   └── llm.py                  # Groq LLM configuration
│
├── db/
│   ├── __init__.py
│   ├── database.py             # SQLite DB logic
│   └── models.py               # Database models
│
├── utils/
│   └── email_utils.py          # Email confirmation logic
│
├── bookings.db                 # SQLite database (auto-created)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Application Flow

### 1️ Chat & Intent Detection
```
User: "I want to book a doctor appointment"
        ↓
System: Detects booking intent
        ↓
Initiates slot-filling conversation
```

### 2️ Slot Filling (Multi-turn Conversation)

The assistant collects the following information in sequence:

1. **Full Name**
2. **Email Address**
3. **Phone Number**
4. **Appointment Date**
5. **Appointment Time**

Each field is validated before moving to the next step.

### 3️ Booking Confirmation

```
Bot: ✅ Booking Details Collected

    Name: Amal Shaji
    Email: amal@gmail.com
    Phone: 8089802312
    Date: 2026-01-22
    Time: 10:00 AM

Type yes to confirm or no to cancel
```

### 4 Booking Completion
- Booking saved to database
- Booking ID generated

---

## Input Validation Rules

| Field | Format | Validation |
|-------|--------|-----------|
| **Email** | `user@example.com` | Valid email format (regex) |
| **Phone** | `9876543210` | 10-digit numeric value |
| **Date** | `YYYY-MM-DD` | Future date only |
| **Time** | `HH:MM AM/PM` | Valid time format |

Invalid inputs trigger user-friendly error messages.

---

## Database Design

### Customers Table
```sql
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Bookings Table
```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    booking_type TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```

---



### Getting API Keys

1. **Groq API Key**
   - Visit: [console.groq.com](https://console.groq.com)
   - Create a new API key
   - Copy and set environment variable


## How to Run the Application

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```



### Step 3: Run Streamlit App
```bash
python -m streamlit run app/main.py
```

### Step 4: Open Browser
```
http://localhost:8501
```

---

## requirements.txt

```txt
streamlit==1.28.0
langchain==0.1.0
langchain-core==0.1.0
langchain-groq==0.1.0
```

Install with:
```bash
pip install -r requirements.txt
```

---

## Sample Booking Conversation

```
User: I want to book a doctor appointment

Bot: What is your full name?
User: Amal Shaji

Bot: Please provide your email address
User: amal@gmail.com

Bot: What is your phone number? (10 digits)
User: 8089802312

Bot: What date would you like to book? (YYYY-MM-DD)
User: 2026-01-22

Bot: What time would you prefer? (HH:MM AM/PM)
User: 10:00 AM

Bot: Booking Details Collected
    Name: Amal Shaji
    Email: amal@gmail.com
    Phone: 8089802312
    Date: 2026-01-22
    Time: 10:00 AM

    Type yes to confirm or no to cancel
User: yes

Bot: Booking confirmed! 
     Booking ID: #BK2026012201
     Confirmation email sent to amal@gmail.com
```

---

## Code Snippets

### 1. Getting Chatbot Response

**File**: `app/main.py`

```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from models.llm import get_chatgroq_model

def get_chat_response(chat_model, messages, system_prompt):
    """
    Sends conversation history to the LLM and returns response
    """
    try:
        formatted_messages = [SystemMessage(content=system_prompt)]

        for msg in messages:
            if msg["role"] == "user":
                formatted_messages.append(
                    HumanMessage(content=msg["content"])
                )
            else:
                formatted_messages.append(
                    AIMessage(content=msg["content"])
                )

        response = chat_model.invoke(formatted_messages)
        return response.content

    except Exception as e:
        return f"Error: {str(e)}"
```

### 2. LLM Configuration

**File**: `models/llm.py`

```python
import os
from langchain_groq import ChatGroq

def get_chatgroq_model(model_name: str = "llama-3.1-8b-instant"):
    """
    Get a Groq chat model instance.
    
    Args:
        model_name: The model name to use
        
    Returns:
        ChatGroq instance
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    return ChatGroq(
        model=model_name,
        temperature=0.7,
        api_key=api_key
    )
```

### 3. Database Operations

**File**: `db/database.py`

```python
import sqlite3
from datetime import datetime

class BookingDatabase:
    def __init__(self, db_path="bookings.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                booking_type TEXT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT DEFAULT 'confirmed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_booking(self, name, email, phone, date, time):
        """Add a new booking to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)',
                (name, email, phone)
            )
            customer_id = cursor.lastrowid
            
            cursor.execute(
                'INSERT INTO bookings (customer_id, date, time) VALUES (?, ?, ?)',
                (customer_id, date, time)
            )
            booking_id = cursor.lastrowid
            
            conn.commit()
            return booking_id
        finally:
            conn.close()
    
    def get_all_bookings(self):
        """Retrieve all bookings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT b.id, c.name, c.email, c.phone, b.date, b.time, b.status, b.created_at
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            ORDER BY b.created_at DESC
        ''')
        
        bookings = cursor.fetchall()
        conn.close()
        return bookings
```

### 4. Input Validation

**File**: `app/main.py` (Validation functions)

```python
import re
from datetime import datetime

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number (10 digits)"""
    return phone.isdigit() and len(phone) == 10

def validate_date(date_str):
    """Validate date format (YYYY-MM-DD) and ensure it's in future"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj > datetime.now()
    except ValueError:
        return False

def validate_time(time_str):
    """Validate time format (HH:MM AM/PM)"""
    pattern = r'^(0[0-9]|1[0-2]):[0-5][0-9]\s(AM|PM)$'
    return re.match(pattern, time_str) is not None
```

---


##  Academic Relevance

This project demonstrates:

 **Conversational AI Design** - Natural language understanding and generation  
 **Slot-Filling Dialogue Systems** - Multi-turn intent-driven conversations  
 **Input Validation** - Robust error handling and user guidance  
 **Database Integration** - SQLite for persistent data storage  
 **Real-world Workflows** - Practical booking system implementation  
 **Admin Data Management** - Dashboard for data visualization  
 **Email Integration** - Automated notifications  
 **Environment & Security** - Safe credential management  


```

## Email Confirmation


After a successful appointment booking, the system sends a confirmation email to the user using Brevo (Sendinblue).
Email is triggered only after the booking is saved
Uses Brevo’s server-side email API (no SMTP)
Booking remains confirmed even if email delivery fails
Errors are handled gracefully without crashing the app
Email credentials are stored securely using Streamlit secrets and are excluded from version control.
```
