# Plant Store 🌿

A Django-based e-commerce platform for plants, featuring product management, order processing, AI plant chat, community blog, and a full custom admin dashboard.

## Screenshots

![Home Page](screenshot/Screenshot%202026-03-21%20201424.png)

![Products Page](screenshot/Screenshot%202026-03-21%20201509.png)

![Admin Dashboard](screenshot/Screenshot%202026-03-21%20201640.png)

## Features

### Products
- Browse and search products by name, description, or category
- Filter by price range, eco-friendly status, and stock availability
- Sort by name, price, or newest
- Product detail page with related products and recently viewed
- Low stock alerts (auto-notifies admin when stock ≤ 5)
- Eco-friendly product tagging

### Shopping & Orders
- Add to cart with quantity and stock validation
- Cart management (update, remove items)
- Checkout with saved shipping address selection
- Order tracking by order number + email (no login required)
- Order history and detailed order view
- Cancel orders (pending/processing only with stock restoration)

### Payments
- Razorpay integration
- Dummy card payment
- Cash on Delivery, PayPal, Bank Transfer
- Payment status tracking (pending, completed, failed, refunded)
- Admin can process refunds with automatic stock restoration

### User Accounts
- Register, login, logout
- Role-based access: Admin and Customer
- Profile with picture, bio, and display name
- Multiple saved addresses (Home, Work, Billing, Shipping, Other)
- Password reset via token (24-hour expiry)

### Community
- Create and browse blog posts (Gardening Tips, DIY, Plant Care, Sustainability, etc.)
- Comment on blog posts
- Upload video posts (file or YouTube/Vimeo URL) with thumbnails
- Community hub with recent blogs and videos

### Plant AI Chat
- AI-powered plant care assistant using Google Gemini API
- Ask questions about plant care and gardening
- Redirects off-topic questions back to plants

### Customer-Admin Live Chat
- Real-time messaging between customers and admin
- Unread message count and read receipts
- Customer profile info visible to admin

### Notifications
- In-app notifications for customers (order updates, welcome, etc.)
- Admin notifications (new orders, low stock, new users, etc.)
- Mark as read, dismiss, unread count badge

### Admin Dashboard
- Overview stats: products, users, orders, monthly revenue
- Manage products and categories (add, edit, delete)
- Manage orders and update order status
- Manage users (create, edit, activate/deactivate, delete)
- Manage blog posts and video content
- Analytics dashboard with date range selection, revenue trends, top products, sales by category
- Export reports as CSV (orders, revenue, customers, products)
- Manage payments with filtering and refund processing
- Configure Google AI API key from the dashboard

## Tech Stack

- Python / Django 4.2
- MySQL
- Razorpay (payments)
- Google Generative AI / Gemini (plant AI chat)
- Pillow (image handling)
- python-dotenv

## Setup

1. Clone the repo
2. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your values:
   ```bash
   cp .env.example .env
   ```
4. (Optional) Create the MySQL database automatically:
   ```bash
   python create_database.py
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Create default roles:
   ```bash
   python create_roles.py
   ```
7. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
8. Collect static files:
   ```bash
   python manage.py collectstatic
   ```
9. Start the development server:
   ```bash
   python manage.py runserver
   ```


## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description | Required |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django secret key (generate a strong random string) | Yes |
| `DJANGO_DEBUG` | Set to `False` in production | Yes |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of allowed hosts | Yes |
| `DB_NAME` | MySQL database name | Yes |
| `DB_USER` | MySQL username | Yes |
| `DB_PASSWORD` | MySQL password | Yes |
| `DB_HOST` | MySQL host (default: `localhost`) | Yes |
| `DB_PORT` | MySQL port (default: `3306`) | Yes |
| `GOOGLE_AI_API_KEY` | Google Generative AI API key for plant chat | No |
| `OPENAI_API_KEY` | OpenAI API key | No |
| `RAZORPAY_KEY_ID` | Razorpay key ID for payments | No |
| `RAZORPAY_KEY_SECRET` | Razorpay key secret for payments | No |
| `EMAIL_HOST` | SMTP host for sending emails | No |
| `EMAIL_HOST_USER` | SMTP username | No |
| `EMAIL_HOST_PASSWORD` | SMTP password | No |
