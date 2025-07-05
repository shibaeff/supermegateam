# AIHack Project - Local Deployment Guide

## Project Overview

This project consists of a Next.js frontend and a Python backend. The frontend is located in the `front/` directory, and the backend is in the `src/` directory. The application provides AI-powered features and a modern UI.

---

## Prerequisites

- **Node.js** (v18 or higher recommended)
- **pnpm** (for frontend package management)
- **Python** (v3.8 or higher)
- **pip** (Python package manager)
- **virtualenv** (recommended for Python dependencies)

---

## Backend Setup (Python)

1. **Navigate to the project root:**
   ```bash
   cd /path/to/aihack
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the backend server:**
   ```bash
   # Example using Flask or FastAPI (update as needed)
   python src/app_backend.py
   ```
   > **Note:** Adjust the run command based on your backend framework (Flask, FastAPI, etc.).

---

## Frontend Setup (Next.js)

1. **Navigate to the frontend directory:**
   ```bash
   cd front
   ```
2. **Install dependencies:**
   ```bash
   pnpm install
   ```
3. **Run the development server:**
   ```bash
   pnpm dev
   ```
   The app will be available at [http://localhost:3000](http://localhost:3000).

---

## Environment Variables

- If your app requires environment variables, create a `.env.local` file in the `front/` directory and add the necessary variables.
- For the backend, create a `.env` file in the root or `src/` directory as needed.

---

## Troubleshooting

- **Port Conflicts:** Make sure ports 3000 (frontend) and your backend port (e.g., 5000 or 8000) are free.
- **Dependency Issues:** Ensure you are using compatible versions of Node.js and Python.
- **Virtual Environment:** Always activate your Python virtual environment before running backend commands.
- **API Connection:** Update frontend API URLs if your backend runs on a different port or host.

---

## License

This project is for internal use and prototyping. Add your license information here if needed.

---

## Contact

For questions or support, contact the project maintainer.
