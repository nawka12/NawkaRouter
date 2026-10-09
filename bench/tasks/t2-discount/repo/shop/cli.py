import argparse
import json
import sys

from shop.pricing import order_total


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compute an order total from a JSON file.")
    parser.add_argument("order", help='path to a JSON file like {"items": [[price, qty], ...]}')
    parser.add_argument("--tax", type=float, default=0.0, help="tax rate as a fraction, e.g. 0.08")
    args = parser.parse_args(argv)
    with open(args.order) as f:
        data = json.load(f)
    items = [tuple(i) for i in data["items"]]
    print(f"{order_total(items, tax_rate=args.tax):.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
