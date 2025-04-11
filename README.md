# FastAPIProject

## Overview

This project provides a framework for building financial analysis applications using FastAPI and SimFin.  It includes functionalities for fetching financial data, performing data analysis, and exposing the results through a REST API.

## Key Features & Benefits

*   **Data Fetching:** Retrieves financial data from SimFin.
*   **Data Analysis:** Calculates key financial ratios and performs statistical analysis.
*   **API Endpoints:** Exposes analysis results through a FastAPI-based REST API.
*   **Modular Design:**  Well-structured code with clear separation of concerns.
*   **Test Coverage:**  Includes unit and integration tests for ensuring reliability.
*   **Environment Variable Configuration**: Allows easy configuration of API keys and data storage paths.

## Prerequisites & Dependencies

Before you begin, ensure you have the following installed:

*   **Python:**  Version 3.7 or higher.
*   **Pip:** Python package installer.
*   **Virtual Environment (optional but recommended):** `virtualenv` or `venv`

**Dependencies:**

The project relies on the following Python packages, which are listed in `requirements.txt`:

*   `fastapi`
*   `uvicorn`
*   `pandas`
*   `requests`
*   `simfin`
*   `numpy`
*   `matplotlib`
*   `python-dotenv`
*   `plotly`

## Installation & Setup Instructions

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/TzoharLary/FastAPIProject.git
    cd FastAPIProject
    ```

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    # Or using virtualenv:
    # virtualenv venv
    ```

3.  **Activate the Virtual Environment:**

    *   **On Linux/macOS:**

        ```bash
        source venv/bin/activate
        ```

    *   **On Windows:**

        ```bash
        venv\Scripts\activate
        ```

4.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Environment Variables:**

    *   Create a `.env` file in the project's root directory.
    *   Add your SimFin API key and desired data directory path:

        ```
        SIMFIN_API_KEY=YOUR_SIMFIN_API_KEY
        DATA_DIR=data/simfin_data/
        ```

        Replace `YOUR_SIMFIN_API_KEY` with your actual SimFin API key. The `DATA_DIR` variable specifies where SimFin data will be stored.  If `DATA_DIR` is not set in the `.env` file, it defaults to `data/simfin_data/`.

## Usage Examples & API Documentation

**Running the API:**

1.  Start the FastAPI application using Uvicorn:

    ```bash
    uvicorn src.main:app --reload
    ```

    This will start the server, typically on `http://127.0.0.1:8000`.

2.  **API Endpoints:**

    *   **`/` (GET):**  Root endpoint - returns a welcome message. Example response:

        ```json
        {"message": "Welcome to the SimFin Analysis API!"}
        ```

    *   **`/analyze/{ticker}` (GET):**  Analyzes financial data for a given stock ticker (e.g., AAPL). Returns financial ratios and a plot as a base64 encoded string. Example usage (replace `AAPL` with a valid ticker):

        ```
        http://127.0.0.1:8000/analyze/AAPL
        ```

        The endpoint calculates and returns financial ratios, along with a historical revenue plot.  The plot data is base64 encoded. The response is a JSON object:

        ```json
        {
            "ticker": "AAPL",
            "financial_ratios": { ... },
            "revenue_plot_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
        }
        ```
    * You can view interactive API documentation at `http://127.0.0.1:8000/docs` or `http://127.0.0.1:8000/redoc` once the server is running.

**Example `data_analysis.py` Usage:**

The `FinancialAnalyzer` class in `src/data_analysis.py` can be used independently to perform financial analysis.  For example:

```python
from src.data_analysis import FinancialAnalyzer

analyzer = FinancialAnalyzer()
ratios = analyzer.calculate_financial_ratios("AAPL")
print(ratios)
```

## Configuration Options

*   **SIMFIN_API_KEY:**  Your SimFin API key.  Must be set in the `.env` file.
*   **DATA_DIR:**  The directory where SimFin data will be stored.  Defaults to `data/simfin_data/` if not set in the `.env` file.

## Contributing Guidelines

We welcome contributions!  Here's how you can contribute:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix: `git checkout -b feature/your-feature-name`.
3.  Implement your changes and add tests.
4.  Ensure all tests pass: `pytest`.
5.  Commit your changes: `git commit -m "Add your commit message"`.
6.  Push to your forked repository: `git push origin feature/your-feature-name`.
7.  Create a pull request.

## License Information

This project does not currently specify a License.  All rights are reserved.

## Acknowledgments

*   SimFin for providing financial data.
*   FastAPI and its contributors for the excellent web framework.
*   Uvicorn for being a fast and reliable ASGI server.