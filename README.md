# Bazaarche

Bazaarche is an e-commerce api project built with FastAPI and PostgreSQL.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.8+
- PostgreSQL

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/m.mohamadi490/bazaarche_api.git
   cd bazaarche
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file with your database credentials and other configuration.

## Usage

1. Start the FastAPI server:
   ```
   uvicorn main:app --reload
   ```
   or
   ```
   fastapi dev main.py
   ```

2. Open your browser and navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to view the API documentation.

## API Documentation

Detailed API documentation is available at the `/docs` endpoint when the server is running.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

[m.mohamadi] - [m.mohamadi490@gmail.com]

Project Link: [https://github.com/mohamadi490/bazaarche_api](https://github.com/mohamadi490/bazaarche_api)