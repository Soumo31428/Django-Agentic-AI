# Django-Agentic-AI — CoolBreeze AC Customer Portal

A Django web application that serves as a customer portal for **CoolBreeze AC**. Users can log in, view their orders, see order details, and check refund history. An AI-driven support agent chat is planned/in progress.

> **Note:** This README documents the features **implemented so far**. Work in progress is noted at the end.

---

## ✨ Features Implemented

- **Authentication**
  - Login / Logout using Django's built-in auth views
  - Custom Bootstrap-based login page
  - Login required to access the orders area (`LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` configured)
  - Demo credentials available on the login page

- **Orders App**
  - **Order List** (`/orders/`) — shows the logged-in user's orders with product name, order date, carrier, amount, and a colored status badge (Pending / Dispatched / Delivered / Cancelled)
  - **Order Detail** (`/orders/<order_id>/`) — shows full order info: status, amount, order date, carrier, tracking number, delivery address, and refund history
  - **Refund History** — displays all refund requests for an order with reason and status (Pending / Approved / Denied)

- **Support Chat UI (Frontend Only)**
  - The order detail page includes an embedded chat widget ("Get Help") with:
    - Typing indicator
    - Message send via `fetch()` to `/support/chat/<order_id>/`
    - Enter-key support
  - ⚠️ **Backend endpoint is not implemented yet** — see *Not Yet Implemented* below.

- **Admin Panel**
  - `Product`, `Order`, `RefundRequest` registered with custom list displays
  - `Conversation`, `Message`, `AgentLog` registered (support models)

---

## 🛠 Tech Stack

| Layer      | Technology                          |
| ---------- | ----------------------------------- |
| Framework  | Django 6.0.7                        |
| Language   | Python                              |
| Database   | MySQL                               |
| Frontend   | Bootstrap 5 (CDN), vanilla JS       |
| Config     | python-decouple (`.env`)            |
| WSGI       | Django WSGI (`ai_employee_main.wsgi`) |

Dependencies are listed in [`requirements.txt`](requirements.txt).

---

## 📁 Project Structure

```
ai_employee/
├── manage.py
├── requirements.txt
├── db.sqlite3                  # SQLite file (dev fallback; MySQL is configured)
├── ai_employee_main/           # Django project settings
│   ├── settings.py             # MySQL via python-decouple, auth redirects
│   ├── urls.py                 # admin, login/logout, orders include
│   └── ...
├── orders/                     # Orders app
│   ├── models.py               # Product, Order, RefundRequest
│   ├── views.py                # orders_list, order_detail
│   ├── urls.py                 # '' and '<int:order_id>/'
│   ├── admin.py                # custom admin list displays
│   └── ...
├── support/                    # Support app (models only so far)
│   ├── models.py               # Conversation, Message, AgentLog
│   ├── views.py                # (empty — to be implemented)
│   └── ...
└── templates/                  # Project-level templates
    ├── login.html              # Custom login page
    ├── orders_list.html        # My Orders page
    └── order_detail.html       # Order detail + chat widget UI
```

---

## 🗄 Database Models

### `orders` app

| Model             | Key Fields                                                                        |
| ----------------- | --------------------------------------------------------------------------------- |
| `Product`         | name, description, price, category, in_stock                                       |
| `Order`           | user (FK), product (FK), product_name, amount, status, carrier, tracking_number, delivery, created_at, updated_at |
| `RefundRequest`   | order (FK), user (FK), reason, status, created_at                                  |

### `support` app

| Model          | Key Fields                                                              |
| -------------- | ----------------------------------------------------------------------- |
| `Conversation` | user (FK), order (FK), created_at                                       |
| `Message`      | conversation (FK), role (`user` / `agent`), content, created_at         |
| `AgentLog`     | conversation (FK), event_type (support / tool_call / tool_result / manager / risk / final), message, created_at |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MySQL (server running with a database created)

### 1. Clone & Setup

```bash
git clone https://github.com/Soumo31428/Django-Agentic-AI.git
cd ai_employee
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the environment (`.env`)

Create a `.env` file in the project root (i.e., alongside `manage.py`) with:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

DB_NAME=your_database_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

> ℹ️ Settings read these values via `python-decouple` (`config()`). Never commit secrets.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create an admin user (optional, for Django admin)

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** — you'll be redirected to the login page.

---

## 🔗 URLs / Routes

| URL               | View                    | Description                              |
| ----------------- | ----------------------- | ---------------------------------------- |
| `/admin/`         | Django admin            | Admin panel                              |
| `/login/`         | `LoginView`             | Login page (custom template)             |
| `/logout/`        | `LogoutView`            | Logout (redirects to `/login/`)          |
| `/orders/`        | `orders_list`           | Logged-in user's order list              |
| `/orders/<id>/`   | `order_detail`          | Order detail + refund history + chat UI  |

### Demo Credentials

The login page includes demo credentials:

```
username: rathan
password: demo1234
```

---

## 🚧 Not Yet Implemented

The following is **planned but not yet built**:

- **AI Agent Chat Backend** — the frontend chat widget posts to `/support/chat/<order_id>/`, but this endpoint is **not implemented**. This is where the agentic AI support flow (support agent, tool calls, manager/risk agents, final reply — see `AgentLog.event_type` choices) will be wired up.
- **Support App Views & URLs** — `support/views.py` is currently empty; no chat view or URL patterns exist yet.
- **Conversation persistence/retrieval in `order_detail`** — the view has commented-out code for loading `Conversation` and previous messages.

---

## 📄 License

*(Add license details here if applicable.)*