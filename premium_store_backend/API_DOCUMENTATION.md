# مستندات API - فروشگاه خدمات پرمیوم

## اطلاعات پایه
- **Base URL (توسعه):** `http://127.0.0.1:8000` یا `http://localhost:8000`
- **روش احراز هویت:** JWT
- **هدر احراز هویت:** `Authorization: JWT <access_token>`
- **مدت اعتبار:** Access Token = ۱۵ دقیقه | Refresh Token = ۱ روز
- **Pagination:** `?page=1` (هر صفحه ۱۰ آیتم)
- **فرمت خطاها:** همیشه JSON + کد وضعیت HTTP استاندارد (400, 401, 404, 500 و ...)
- **تصاویر:** همه به صورت `image_url` (لینک کامل مستقیم) برگردانده می‌شوند.

## ۱. Authentication (ثبت‌نام و ورود)

- **POST** `/auth/users/` → ثبت‌نام  
  Body: `{ "username": "", "email": "", "password": "" }`  
  Success 201: `{ "id": , "username": , "email": }`

- **POST** `/auth/jwt/create/` → ورود  
  Body: `{ "username": "", "password": "" }`  
  Success 200: `{ "access": "...", "refresh": "..." }`

- **POST** `/auth/jwt/refresh/` → رفرش توکن  
  Body: `{ "refresh": "..." }`

## ۲. Customer (اطلاعات کاربر و شماره موبایل)

- **GET/PATCH** `/customers/me/` → گرفتن/آپدیت اطلاعات کاربر  
  (بعد از لاگین حتماً این آدرس را PATCH کن و شماره موبایل اضافه کن)

- **POST** `/customers/verify-phone/` → تأیید کد OTP  
  Body: `{ "code": "123456" }`

- **POST** `/customers/resend-otp/` → ارسال مجدد کد

## ۳. Applications

- **GET** `/applications/` → لیست اپلیکیشن‌ها (صفحه‌بندی شده)
- **GET** `/applications/<id>/` → جزئیات یک اپلیکیشن

## ۴. Services (محصولات)

- **GET** `/applications/<application_id>/services/` → لیست خدمات یک اپلیکیشن  
  پارامترها: `?search=...&price__range=100000,200000&ordering=price&discounts=1`

- هر سرویس شامل فیلدهای:  
  `id, name, description, price, discounted_price, image_url, required_fields (آرایه), discounts`

## ۵. Cart و Cart Items

- **POST** `/carts/` → ایجاد سبد خرید جدید  
- **GET** `/carts/<cart_id>/` → جزئیات سبد خرید (شامل items و total_cart_price)

- **POST** `/carts/<cart_id>/items/` → اضافه کردن سرویس به سبد  
  Body: `{ "service": <service_id>, "quantity": 1, "extra_data": { "username": "...", "password": "..." } }`

- **PATCH** `/carts/<cart_id>/items/<item_id>/` → ویرایش تعداد یا extra_data  
- **DELETE** `/carts/<cart_id>/items/<item_id>/` → حذف آیتم

## ۶. Orders و پرداخت

- **POST** `/orders/` → ایجاد سفارش از سبد خرید  
  Body: `{ "cart_id": "uuid سبد خرید" }`

- **POST** `/orders/<order_id>/pay/` → شروع پرداخت (Zarinpal)  
  Success: `{ "payment_url": "https://..." }`

- **GET** `/orders/<order_id>/callback/` → برگشت از درگاه (callback)

- **GET** `/orders/` → لیست سفارش‌های کاربر (فیلتر: `?status=p|u|c`)

## نکات مهم
- برای ثبت سفارش، حتماً شماره موبایل تأیید شده داشته باشید.
- extra_data باید دقیقاً فیلدهای required_fields سرویس را پر کند.
- تصاویر همیشه از فیلد `image_url` استفاده کنید (لینک کامل).
- تمام خطاهای validation به صورت JSON با کلیدهای فیلد یا "detail" برمی‌گردد.

آخرین به‌روزرسانی: ۲۸ ژانویه ۲۰۲۶