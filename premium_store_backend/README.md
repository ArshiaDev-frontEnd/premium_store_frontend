# Premium Services Store API

This is a Django Rest Framework (DRF) based e-commerce API for selling premium subscription services for platforms like Telegram, Spotify, YouTube, and more. Users can browse applications (categories), select services, add them to a cart with custom fields (e.g., username, password), proceed to checkout, and complete payments via Zarinpal gateway. It includes features like user authentication, phone verification via SMS (using Kavenegar), discounts, order management, and admin controls. The project is containerized with Docker for easy deployment and uses Celery for asynchronous tasks like SMS sending.

This repository serves as a strong portfolio piece demonstrating full-stack API development, including secure authentication, payment integration, and scalable architecture.

## Developers
**Backend Developer:**
[Sina Khalafi](https://github.com/SinaCode-dev)

**Frontend Developer:**
[Arshia Karimi Jabali](https://github.com/ArshiaDev-frontEnd)

---
Built with ❤️ by backend and frontend team

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Contact](#contact)

## Features
- **User Authentication**: JWT-based login/register via Djoser, with phone number verification using OTP sent via SMS (Kavenegar integration).
- **Product Catalog**: Applications (categories) and Services with images, descriptions, prices, discounts, and custom required fields (e.g., email, username for premium activations).
- **Shopping Cart**: Add/remove/update items with quantity and extra data (e.g., account credentials). Supports validation for required fields before checkout.
- **Order Management**: Create orders from carts, track status (paid/unpaid/canceled), and view order history. Admins can manage orders.
- **Payment Integration**: Zarinpal gateway for Iranian payments, with sandbox mode support.
- **Discounts**: Apply percentage-based discounts to services.
- **Comments**: Users can leave comments on services, with moderation (approved/waiting/not approved).
- **Admin Panel**: Django admin for managing customers, applications, services, discounts, orders, and more.
- **Filtering & Pagination**: Search, filter (e.g., by price, discount), order, and paginate services/orders.
- **Asynchronous Tasks**: Celery with Redis for background jobs like SMS sending.
- **Security**: Permissions for admin-only actions, validation for required fields, and secure handling of sensitive data (e.g., passwords in extra_data).
- **Media Handling**: Upload and serve images for applications/services.
- **Dockerized**: Ready for production with Docker Compose (Postgres, Redis, Celery worker).

## Tech Stack
- **Backend**: Django 5.0, Django Rest Framework (DRF)
- **Database**: PostgreSQL (with psycopg2-binary)
- **Caching & Queues**: Redis (for Celery broker/result backend)
- **Task Queue**: Celery (for async SMS sending)
- **Authentication**: Djoser + SimpleJWT
- **Payments**: Zarinpal (Iranian gateway)
- **SMS**: Kavenegar API
- **Other Libraries**: django-environ (env management), django-filter, phonenumber-field, Pillow (image processing), debug-toolbar
- **Containerization**: Docker & Docker Compose
- **Deployment Tools**: .dockerignore, .gitignore, requirements.txt

## Installation

### Prerequisites
- Docker & Docker Compose (for containerized setup)
- Git
- Python 3.12+ (if running locally without Docker)
- Environment variables: Create a `.env` file based on the example below.

#### .env Example
SECRET_KEY=your-secret-key

DEBUG=True

ALLOWED_HOSTS=127.0.0.1,localhost

POSTGRES_DB=yourdb

POSTGRES_USER=youruser

POSTGRES_PASSWORD=yourpass

POSTGRES_HOST=db

POSTGRES_PORT=5432

ZARINPAL_MERCHANT_ID=your-merchant-id

ZARINPAL_SANDBOX=True

ZARINPAL_REQUEST_URL=https://sandbox.zarinpal.com/pg/services/WebGate/wsdl

ZARINPAL_VERIFY_URL=https://sandbox.zarinpal.com/pg/services/WebGate/wsdl

ZARINPAL_START_PAY_URL=https://sandbox.zarinpal.com/pg/StartPay/

ZARINPAL_CALLBACK_URL=http://localhost:8000/api/orders/pay/callback/

KAVENEGAR_API_KEY=your-kavenegar-key

KAVENEGAR_SENDER=your-sender-number

CELERY_BROKER_URL=redis://redis:6379/0

CELERY_RESULT_BACKEND=redis://redis:6379/0

CELERY_ACCEPT_CONTENT=application/json

CELERY_TASK_SERIALIZER=json

CELERY_RESULT_SERIALIZER=json

CELERY_TIMEZONE=UTC


### With Docker (Recommended)
1. Clone the repository:
2. Build and start containers:
3. Apply migrations and create superuser:


4. Access the API at `http://localhost:8000/` and admin at `http://localhost:8000/admin/`.

### Locally (Without Docker)
1. Clone the repo and navigate to it.
2. Create a virtual environment:
3. Install dependencies:
4. Set up the database (e.g., PostgreSQL) and Redis.
5. Run migrations and superuser:
6. Start the server:


Start Celery worker separately: `celery -A config worker --loglevel=info`

## Usage
- **Register/Login**: Use `/auth/users/` for registration and `/auth/jwt/create/` for login.
- **Browse Services**: GET `/applications/` or `/applications/<app_pk>/services/`.
- **Cart Operations**: POST to `/carts/` to create a cart, then add items via `/carts/<cart_pk>/items/`.
- **Checkout**: POST to `/orders/` with cart ID, then proceed to payment.
- **Payment**: After order creation, redirect to Zarinpal URL. Callback handles verification.
- **Phone Verification**: Update phone in `/customers/me/`, then verify OTP via `/customers/verify-phone/`.
- **Admin**: Access Django admin for CRUD on models.

For full API documentation, use tools like Swagger (not included, but can be added via drf-yasg).

## API Endpoints
- `/applications/`: List/create applications.
- `/applications/<pk>/services/`: Services under an application.
- `/carts/`: Manage carts.
- `/carts/<pk>/items/`: Cart items.
- `/orders/`: List/create orders.
- `/orders/<pk>/items/`: Order items.
- `/discounts/`: Manage discounts.
- `/customers/me/`: User profile (including phone verification).
- More nested routes for comments, etc. (see `store/urls.py`).

## Project Structure
.
├── store/                # Main app: models, views, serializers, etc.

│   ├── migrations/       # Database migrations

│   ├── static/           # Static files (e.g., default images)

│   ├── admin.py          # Django admin config

│   ├── models.py         # Database models

│   ├── serializers.py    # DRF serializers

│   ├── views.py          # API views

│   ├── urls.py           # API routes

│   └── ...

├── core/                 # Custom user model app

├── config/               # Project settings

│   ├── settings.py       # Django settings

│   ├── urls.py           # Root URLs

│   └── ...

├── media/                # Uploaded media (e.g., images)

├── docker-compose.yml    # Docker setup

├── Dockerfile            # Backend container config

├── requirements.txt      # Dependencies

├── .env                  # Environment variables (not committed)

├── .dockerignore         # Docker ignore rules

└── .gitignore            # Git ignore rules



## Contributing
Contributions are welcome! Please fork the repo, create a feature branch, and submit a PR. Ensure tests pass (add pytest if needed) and follow PEP8.


## Contact
- LinkedIn: [your-linkedin](https://linkedin.com/in/yourname)

Feel free to star the repo if you find it useful! 🚀
