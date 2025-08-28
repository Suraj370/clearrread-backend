# Dyslexic Converter Backend Documentation

## Problem It Solves

Dyslexia is a learning disorder that affects reading and related language-based processing skills. People with dyslexia often struggle with standard text formats due to issues like letter spacing, font style, and visual crowding. This FastAPI backend addresses this problem by providing a service to convert regular text into a dyslexia-friendly format (referred to as "dyslexic" conversion). This could involve using specialized fonts (e.g., OpenDyslexic), adjusted spacing, color contrasts, or other techniques to improve readability. Additionally, it supports document creation and editing, allowing users to manage and modify content in a way that's tailored for accessibility. The backend likely serves as the server-side component for a larger application, such as a web or mobile app aimed at assisting dyslexic users in reading and writing.

## APIs Created

Based on the project's focus on document creation, editing, and text conversion, the backend exposes several RESTful APIs built with FastAPI. FastAPI is chosen for its high performance, automatic interactive documentation (via Swagger UI), and type validation using Pydantic models. The APIs are designed to handle requests for managing documents and performing conversions.

Here is a list of the primary APIs, their methods, endpoints, and functionalities (inferred from the project description; exact details may vary based on implementation):

1. **Create Document API**
   - **Method**: POST
   - **Endpoint**: `/documents` (or similar, e.g., `/api/v1/documents`)
   - **Description**: This API allows users to create a new document. It accepts input such as the document title, content (text), and possibly metadata like user ID or format preferences. The backend processes the request, potentially stores the document in a database (e.g., SQLite, PostgreSQL, or MongoDB), and returns a unique document ID along with the created document details.
   - **Request Body Example** (JSON):
     ```json
     {
       "title": "My First Document",
       "content": "This is the initial text."
     }
     ```
   - **Response Example** (JSON):
     ```json
     {
       "id": "12345",
       "title": "My First Document",
       "content": "This is the initial text.",
       "created_at": "2025-08-28T12:00:00Z"
     }
     ```
   - **Use Case**: Useful for starting a new readable document from scratch.

2. **Edit Document API**
   - **Method**: PUT or PATCH
   - **Endpoint**: `/documents/{document_id}` (or similar, e.g., `/api/v1/documents/{id}`)
   - **Description**: This API enables updating an existing document. It requires the document ID in the path and accepts updated fields like new content or title in the request body. The backend retrieves the document, applies the changes, saves them, and returns the updated document. This supports iterative editing for users refining their text.
   - **Request Body Example** (JSON):
     ```json
     {
       "content": "This is the updated text with changes."
     }
     ```
   - **Response Example** (JSON):
     ```json
     {
       "id": "12345",
       "title": "My First Document",
       "content": "This is the updated text with changes.",
       "updated_at": "2025-08-28T12:30:00Z"
     }
     ```
   - **Use Case**: Allows dyslexic users to revise documents without losing previous work.

3. **Convert Text to Dyslexic Format API**
   - **Method**: POST
   - **Endpoint**: `/convert-text/` 
   - **Description**: This core API takes plain text as input and converts it into a dyslexia-friendly format. The conversion logic might include applying special formatting, such as increased letter spacing, using dyslexia-specific fonts, or other enhancements. It returns the converted text, which can be displayed in a frontend app. Optionally, it could accept parameters for customization (e.g., font type, spacing level).
   - **Request Body Example** (JSON):
     ```json
     {
       "text": "This is sample text to convert."
     }
     ```
   - **Response Example** (JSON):
     ```json
     {
       "converted_text": "T h i s  i s  s a m p l e  t e x t  t o  c o n v e r t ."  // Example with added spacing
     }
     ```
   - **Use Case**: Instant conversion for any text input, making reading easier for dyslexic individuals.

FastAPI automatically provides interactive docs at `/docs` (Swagger UI) and `/redoc` for exploring these endpoints.

## How to Run

To run the backend locally, follow these steps (assuming a standard FastAPI setup; adjust based on any custom configurations in the repo):

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Suraj370/clearrread-backend.git
   cd clearrread-backend
   ```

2. **Set Up a Virtual Environment** (Recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   The project likely uses a `requirements.txt` file. Install the packages:
   ```bash
   pip install -r requirements.txt
   ```
   Common dependencies for FastAPI include `fastapi`, `uvicorn` (ASGI server), `pydantic`, and possibly others like `sqlalchemy` for DB or libraries for text conversion.

4. **Configure Environment** (If Applicable):
   - Set environment variables if needed (e.g., for database connection: `DATABASE_URL`).
   - If using a database, initialize it (e.g., run migrations if using Alembic).

5. **Run the Application**:
   Use Uvicorn to start the server:
   ```bash
   uvicorn app.main:app --reload  # Assumes the FastAPI app is in app/main.py; adjust if different (e.g., main:app)
   ```
   - `--reload`: Enables auto-reloading for development.
   - The server will run on `http://127.0.0.1:8000` by default.
   - Access the API docs at `http://127.0.0.1:8000/docs`.

6. **Testing**:
   - Use tools like Postman, curl, or the built-in Swagger UI to test the endpoints.
   - For production, deploy to a platform like Heroku, Vercel, or AWS, and use a production ASGI server like Gunicorn + Uvicorn.

If the repository includes a Dockerfile, you can build and run it as a container:
```bash
docker build -t clearrread-backend .
docker run -p 8000:8000 clearrread-backend
```

For any specific setup details (e.g., custom ports, DB setup), refer to comments in the code or a README file if added to the repo. If encountering issues, ensure Python 3.8+ is installed.