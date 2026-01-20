# Sale System API Reference

This document provides a detailed reference for the RESTful APIs of the Sale System.

## 1. Authentication & Authorization

The system uses JWT (JSON Web Tokens) for authentication.

- **Storage**: Tokens are primarily stored in an `HttpOnly` cookie (configured via `JWT_COOKIE_NAME`). The system also supports the `Authorization: Bearer <token>` header.
- **Roles**:
  - `admin`: Full access to all resources.
  - `vendor`: Access to sales data and product management. Can be "Global" (access to all events) or "Event-Scoped" (restricted to a specific `event_id`).
- **Token Payload**: Includes `role`, `access` ('all' or 'event'), `event_id` (if scoped), and standard claims (`exp`, `iat`, `iss`).

### Login
- **POST `/api/auth/login`**
  - **Body**:
    ```json
    {
      "role": "admin" | "vendor",
      "password": "...",
      "eventId": 123 // Optional, used for event-scoped vendor login
    }
    ```
  - **Logic**:
    - `admin`: Matches `ADMIN_PASSWORD`. Returns `access: "all"`.
    - `vendor`:
      - Matches `ADMIN_PASSWORD` or `VENDOR_PASSWORD`: Returns `access: "all"`.
      - Matches `Event.vendor_password` (if `eventId` provided): Returns `access: "event"` and `eventId`.
  - **Success Response (200)**: Sets cookie and returns:
    ```json
    {
      "message": "...",
      "role": "admin" | "vendor",
      "access": "all" | "event",
      "eventId": 123 // if applicable
    }
    ```
  - **Errors**: 400 (Missing fields), 401 (Invalid password).

---

## 2. Server Information

- **GET `/api/server-info`** (Public)
  - Returns LAN connection details for mobile devices.
  - **Response**:
    ```json
    {
      "ip": "192.168.1.10",
      "port": 5000,
      "base_url": "http://192.168.1.10:5000",
      "order_url": "...",
      "vendor_url": "...",
      "admin_url": "..."
    }
    ```

---

## 3. Event Management

- **GET `/api/events`** (Public)
  - **Query Params**: `status` (optional: `未进行`, `进行中`, `已结束`).
  - **Response**: List of Event objects.
    ```json
    {
      "id": 1,
      "name": "...",
      "date": "2026-01-02",
      "location": "...",
      "status": "进行中",
      "qrcode_url": "/static/uploads/..."
    }
    ```

- **GET `/api/events/{eventId}`** (Public)
  - **Response**: Single Event object (same structure as above).

- **POST `/api/events`** (Admin)
  - **Content-Type**: `multipart/form-data`
  - **Fields**: `name` (req), `date` (req, `YYYY-MM-DD`), `location`, `vendor_password`, `payment_qr_code` (file).
  - **Response (201)**: Created Event object.

- **PUT `/api/events/{eventId}/status`** (Admin)
  - **Body**: `{ "status": "..." }`
  - **Response (200)**: Updated Event object.

- **PUT|POST `/api/events/{eventId}`** (Admin)
  - **Content-Type**: `multipart/form-data`
  - **Fields**: `name`, `date`, `location`, `vendor_password`, `remove_payment_qr_code` ("true"), `payment_qr_code` (file).
  - **Response (200)**: Updated Event object.

- **DELETE `/api/events/{eventId}`** (Admin)
  - Deletes event and associated files.

---

## 4. Master Product Catalog (Global)

- **GET `/api/master-products`** (Public)
  - **Query Params**: `all` (boolean, default false).
  - **Response**: List of MasterProduct objects.
    ```json
    {
      "id": 1,
      "product_code": "P001",
      "name": "...",
      "default_price": 100.0,
      "image_url": "/static/uploads/products/...",
      "is_active": true,
      "category": "..."
    }
    ```

- **POST `/api/master-products`** (Admin)
  - **Content-Type**: `multipart/form-data`
  - **Fields**: `product_code` (req, unique), `name` (req), `default_price` (req), `category`, `image` (file).
  - **Response (201)**: Created MasterProduct.

- **PUT|POST `/api/master-products/{id}`** (Admin)
  - **Content-Type**: `multipart/form-data`
  - **Fields**: `product_code`, `name`, `default_price`, `category`, `remove_image` ("true"), `image` (file).
  - **Response (200)**: Updated MasterProduct.

- **PUT `/api/master-products/{id}/status`** (Admin)
  - **Body**: `{ "is_active": boolean }`
  - **Response (200)**: Updated MasterProduct.

---

## 5. Event Inventory (Products)

- **GET `/api/events/{eventId}/products`** (Public)
  - **Response**: List of Product objects.
    ```json
    {
      "id": 10,
      "master_product_id": 1,
      "product_code": "P001",
      "name": "...",
      "price": 95.0,
      "initial_stock": 50,
      "current_stock": 45,
      "image_url": "...",
      "event_id": 123,
      "category": "..."
    }
    ```

- **POST `/api/events/{eventId}/products`** (Admin/Vendor Scoped)
  - **Body**: `{ "product_code": "...", "initial_stock": 10, "price": 99.0 }`
  - **Logic**: Links a MasterProduct to an Event. `price` defaults to `default_price`.
  - **Response (201)**: Created Product object.

- **PUT `/api/products/{productId}`** (Admin/Vendor Scoped)
  - **Body**: `{ "price": 88.0, "initial_stock": 20 }`
  - **Response (200)**: Updated Product object.

- **DELETE `/api/products/{productId}`** (Admin/Vendor Scoped)
  - Removes product from event.

---

## 6. Order Processing

- **POST `/api/events/{eventId}/orders`** (Public)
  - **Body**:
    ```json
    {
      "items": [
        { "product_id": 1, "quantity": 2 },
        { "product_id": 2, "quantity": 1 }
      ]
    }
    ```
  - **Logic**:
    - Atomic transaction.
    - **Stock Check**: `available_stock = initial_stock - (pending_qty + completed_qty)`.
    - If stock < requested, returns **406 Not Acceptable**.
  - **Response (201)**: Created Order object.
    ```json
    {
      "id": 500,
      "timestamp": "2026-01-02T10:00:00",
      "status": "pending",
      "total_amount": 290.0,
      "event_id": 123,
      "items": [
        {
          "id": 1001,
          "quantity": 2,
          "product_id": 1,
          "product_name": "...",
          "product_price": 95.0,
          "product_image_url": "..."
        }
      ]
    }
    ```

- **GET `/api/events/{eventId}/orders`** (Admin/Vendor Scoped)
  - **Query Params**: `status` (optional: `pending`, `completed`, `cancelled`).
  - **Response**: List of Order objects (same structure as above).

- **PUT `/api/events/{eventId}/orders/{orderId}/status`** (Admin/Vendor Scoped)
  - **Body**: `{ "status": "..." }`
  - **Response (200)**: Updated Order object.

---

## 7. Statistics & Reports

- **GET `/api/events/{eventId}/stats`** (Admin/Vendor Scoped)
  - **Response**:
    ```json
    {
      "event_info": { ... },
      "summary": {
        "total_revenue": 1234.5,
        "completed_orders_count": 10,
        "total_items_sold": 50
      },
      "product_details": [
        { "product_id": 1, "name": "...", "sold_count": 5, "revenue": 500.0, ... }
      ]
    }
    ```

- **GET `/api/events/{eventId}/sales_summary`** (Admin/Vendor Scoped)
  - **Query Params**: `product_code`, `start_date`, `end_date`, `interval_minutes` (30 or 60).
  - **Response**: Detailed summary including revenue timeseries.

- **GET `/api/events/{eventId}/sales_summary/download`** (Admin/Vendor Scoped)
  - **Response**: Binary stream (Excel file).

---

## 8. Common Error Codes

| Code | Meaning | Description |
|---|---|---|
| 400 | Bad Request | Missing required fields or invalid data format. |
| 401 | Unauthorized | Missing or invalid JWT token / Incorrect password. |
| 403 | Forbidden | Insufficient role or trying to access an event not authorized for the vendor. |
| 404 | Not Found | Resource (Event, Product, Order) does not exist. |
| 406 | Not Acceptable | Stock insufficient for the requested order. |
| 409 | Conflict | Duplicate resource (e.g., product code already exists). |
| 500 | Internal Error | Server-side exception. |
