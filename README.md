Premium Services Store API
This is a Django Rest Framework (DRF) based e-commerce API for selling premium subscription services for platforms like Telegram, Spotify, YouTube, and more. Users can browse applications (categories), select services, add them to a cart with custom fields (e.g., username, password), proceed to checkout, and complete payments via Zarinpal gateway. It includes features like user authentication, phone verification via SMS (using Kavenegar), discounts, order management, and admin controls. The project is containerized with Docker for easy deployment and uses Celery for asynchronous tasks like SMS sending.

This repository serves as a strong portfolio piece demonstrating full-stack API development, including secure authentication, payment integration, and scalable architecture.

Developers
Backend Developer: [Sina Khalafi](https://github.com/SinaCode-dev)

Frontend Developer: [Arshia Karimi Jabali](https://github.com/ArshiaDev-frontEnd)


## 🛠 Tech Stack

* **Framework:** React / Next.js (Tailored for SEO and performance)
* **Styling:** Tailwind CSS (For clean, maintainable, and modern styling)
* **State Management:** Redux Toolkit / Zustand
* **API Client:** Axios (With interceptors for professional request handling)
* **Form Validation:** Formik / React Hook Form with Yup/Zod

## 📂 Project Structure

```text
src/
├── components/   # Reusable UI components
├── pages/        # Application routes and views
├── services/     # API calls and backend communication
├── store/        # Global state management
├── assets/       # Images, icons, and global styles
└── hooks/        # Custom React hooks for logic reuse
