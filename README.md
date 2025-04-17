# Ghostly - Dynamic Content Access Protection

Ghostly is a secure content access protection service that uses time-limited tokens to protect digital assets from unauthorized access and misuse.

![Workflow Diagram](https://raw.githubusercontent.com/Optimus-Labs/ghostly/main/assets/workflow.png)

## 🔑 Key Features

- **Dynamic Token Generation:** Create time-bound access tokens linked to specific users, sessions, or devices
- **Tamper-Proof Security:** Tokens automatically expire and cannot be reused or modified
- **Simple API Integration:** Single API call to generate secure access links
- **Comprehensive Analytics:** Track content access with built-in logging and monitoring
- **Scalable Architecture:** Built on modern, high-performance technologies

## 🚀 Unique Selling Points

- **Developer-First Design:** Minimal implementation overhead with just one API call
- **No Custom Validation Required:** Eliminate complex security code from your application
- **Automated Security:** Set-and-forget content protection that works silently in the background
- **Real-Time Insights:** Detailed analytics on content access patterns and potential security threats
- **Flexible Deployment:** Run as a service or self-host for complete control

## 🔧 Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PyJWT, passlib, cryptography
- **Database:** PostgreSQL, Redis
- **Dependencies:** Cloudflare Workers, Fernet

## 🚦 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Git

### Installation

#### Windows

```bash
# Clone the repository
git clone https://github.com/Optimus-Labs/ghostly.git
cd ghostly

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

#### Linux/macOS

```bash
# Clone the repository
git clone https://github.com/Optimus-Labs/ghostly.git
cd ghostly

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

## 🔌 API Usage

Once the server is running, you can access the API documentation at `http://localhost:8000/docs`.

### Basic Example

```python
import requests

# Generate a secure access token
response = requests.post(
    "http://localhost:8000/api/v1/tokens/generate",
    json={
        "content_id": "your-content-id",
        "user_id": "user-123",
        "expiry": 3600  # Token valid for 1 hour
    },
    headers={"X-API-Key": "your-api-key"}
)

# Get the secure access link
secure_link = response.json()["secure_link"]

# Share this link with your user for secure access
print(f"Secure access link: {secure_link}")
```

## 📊 Dashboard & Analytics

Ghostly provides a comprehensive analytics dashboard that includes:

- Token usage statistics
- Access patterns visualization
- Security alerts for suspicious activities
- Detailed logs for audit purposes

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.