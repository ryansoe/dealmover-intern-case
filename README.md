## Getting Started

You'll need to run both the backend and frontend servers. Here's how:

### Backend Setup (Django)

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the Django development server:
   ```bash
   python manage.py runserver
   ```

The backend API will be available at `http://127.0.0.1:8000`

### Frontend Setup (React)

1. Open a new terminal and navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:

   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173` (or whatever port Vite assigns)

## Using the Application

1. Make sure both servers are running
2. Open your browser to the frontend URL
3. Upload a PDF file (try the included `Form 10-K.pdf` for testing)
4. Optionally select a period end date
5. Click "Extract Data" and wait for the results

The app will show you a table with the revenue and calculated gross profit for the selected period.

## Technical Notes

- The backend uses regex patterns to extract financial data from PDF text
- The frontend communicates with the backend via a REST API
- PDF processing is handled by the `pdfplumber` library
- Environment variables can be configured in `frontend/.env` for different deployment environments

## Troubleshooting

**Backend won't start?** Make sure you have Python 3.x installed and all requirements are installed correctly.

**Frontend won't start?** Check that you have Node.js installed and try deleting `node_modules` and running `npm install` again.

**Can't extract data?** The regex patterns are designed for specific financial document formats. Different PDF structures might not work as expected.
