# AI Customer Support Refund Agent

Built with: **Anthropic Claude API** (raw function calling), **FastAPI**, vanilla HTML/JS

## Setup & Installation

### 1. Dependency Installation
Ensure Python dependencies are installed in your virtual environment:
```bash
# Activate your virtual environment
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install backend packages
pip install -r backend/requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the project root:
```env
ANTHROPIC_API_KEY=your_key_here
```
*(If no key is configured, the application will automatically run in local **Simulation Mode** fallback with high-fidelity mock tools so you can test all features immediately.)*

---

## Running the Application

### Option A: Run Both Concurrently (Recommended)
You can launch both the FastAPI backend and http-server frontend together using a single command:
```bash
npm run dev
```
* **Frontend Dashboard**: Open [http://localhost:3000](http://localhost:3000)
* **Backend API**: Runs at [http://localhost:8000](http://localhost:8000)

### Option B: Run Backend & Frontend Separately

#### Run Backend:
```bash
npm run backend
# Or manually:
cd backend && ../venv/bin/uvicorn main:app --reload
```

#### Run Frontend:
```bash
npm run frontend
# Or manually (serves app.html by default):
npx -y http-server frontend -p 3000 -c-1 -i app.html
```

## Test Orders

| Order ID | Scenario                                |
| -------- | --------------------------------------- |
| ORD001   | ✅ Damaged item - APPROVED              |
| ORD002   | ❌ Digital product - DENIED             |
| ORD003   | ❌ Used item - DENIED                   |
| ORD004   | ✅ Not delivered - APPROVED             |
| ORD005   | ❌ Sale item - DENIED                   |
| ORD006   | ✅ Wrong item - APPROVED                |
| ORD007   | ❌ Expired window - DENIED              |
| ORD008   | ❌ Already refunded in 90 days - DENIED |
