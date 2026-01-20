# Backend Data Models

Summary of the SQLAlchemy models defined in `backend/app/models.py`.

## Event
- Fields: `id`, `name` (required), `date` (required), `location`, `status` (required, default `未进行`, indexed), `vendor_password` (optional), `qrcode_url`.
- Relationships: `products` (one-to-many Product, cascade delete), `orders` (one-to-many Order, cascade delete).
- Methods: `to_dict()` returns basic event info including status and QR code URL.

## MasterProduct
- Purpose: Global product catalog entries reused across events.
- Fields: `id`, `product_code` (unique, indexed), `name` (required), `default_price` (required), `image_url`, `is_active` (required, default True, indexed), `category` (indexed).
- Relationships: `products` (one-to-many Product, cascade delete).
- Methods: `to_dict()` exports base product info.

## Product
- Purpose: Event-specific product listing linked to both an event and a master product; acts like inventory per event.
- Fields: `id`, `price` (required), `initial_stock` (required), `event_id` (FK -> Event), `master_product_id` (FK -> MasterProduct).
- Constraints: Unique `(event_id, master_product_id)` to avoid duplicate listings per event.
- Derived properties:
  - `sold_count`: Sum of `OrderItem.quantity` for completed orders.
  - `current_stock`: `initial_stock - sold_count`.
  - `name`: Mirrors linked master product name or "未知商品" if missing.
- Methods: `to_dict()` combines event-specific pricing/stock with master product data (code, name, image, category).

## Order
- Fields: `id`, `timestamp` (default to Beijing time UTC+8, indexed), `status` (default `pending`), `total_amount` (required), `event_id` (FK -> Event).
- Relationships: `items` (one-to-many OrderItem, cascade delete).
- Methods: `to_dict()` includes order metadata and serialized items.

## OrderItem
- Fields: `id`, `quantity` (required), `order_id` (FK -> Order), `product_id` (FK -> Product).
- Relationships: `product` (direct link to Product).
- Methods: `to_dict()` returns item details plus denormalized product name, price, and image from the linked master product.
