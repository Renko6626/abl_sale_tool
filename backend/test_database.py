"""
Quick helper script to dump all data from the SQLite database (app.db).

Usage:
	python test_database.py

This will create the Flask app context, query every table, and print rows
as dictionaries. Safe to run read-only; it does not modify the database.
"""

from pprint import pprint

from app import create_app, db
from app.models import Event, MasterProduct, Order, OrderItem, Product


def _print_rows(title: str, rows):
	print(f"\n=== {title} ({len(rows)} rows) ===")
	if not rows:
		print("<empty>")
		return
	for row in rows:
		# Most models already provide to_dict; fallback to __dict__ for others.
		if hasattr(row, "to_dict"):
			pprint(row.to_dict())
		else:
			pprint({k: v for k, v in row.__dict__.items() if not k.startswith("_")})


def main():
	app = create_app()
	with app.app_context():
		_print_rows("Events", Event.query.all())
		_print_rows("MasterProducts", MasterProduct.query.all())
		_print_rows("Products", Product.query.all())
		_print_rows("Orders", Order.query.all())
		_print_rows("OrderItems", OrderItem.query.all())


if __name__ == "__main__":
	main()
