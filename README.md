# Flask E-commerce Store

A modern e-commerce platform built with Flask, using Blueprints for modular organization.

## Features

- User authentication (login/register)
- Product catalog
- Shopping cart functionality
- Responsive design with Bootstrap
- SQLite database (can be configured for other databases)

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///ecommerce.db
```

4. Initialize the database:
```bash
flask shell
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
├── app.py              # Main application file
├── config.py           # Configuration settings
├── requirements.txt    # Project dependencies
├── models/            # Database models
│   ├── user.py
│   ├── product.py
│   └── cart.py
├── routes/            # Route blueprints
│   ├── main.py
│   ├── auth.py
│   ├── products.py
│   └── cart.py
├── static/            # Static files
│   ├── css/
│   ├── js/
│   └── uploads/
└── templates/         # Jinja2 templates
    ├── base.html
    ├── auth/
    ├── products/
    └── cart/
```

## License

MIT 