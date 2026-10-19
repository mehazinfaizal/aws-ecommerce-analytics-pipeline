import csv
import io
import json
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation

import boto3

s3 = boto3.client("s3")

BUCKET = os.environ["BUCKET_NAME"]

SOURCE_KEY = "raw/online-retail/Online Retail.csv"
OUTPUT_KEY = "curated/sales/online_retail_clean.csv"
REJECTED_KEY = "rejected/online_retail_rejected.csv"


def lambda_handler(event, context):
    response = s3.get_object(Bucket=BUCKET, Key=SOURCE_KEY)

    # This public dataset's common CSV export may use Windows-1252 encoding.
    source = io.TextIOWrapper(
        response["Body"],
        encoding="cp1252",
        newline=""
    )
    reader = csv.DictReader(source)

    output = io.StringIO(newline="")
    rejected = io.StringIO(newline="")

    columns = [
        "invoice_no",
        "stock_code",
        "description",
        "quantity",
        "invoice_timestamp",
        "unit_price",
        "customer_id",
        "country",
        "total_amount",
    ]

    writer = csv.DictWriter(output, fieldnames=columns)
    reject_writer = csv.writer(rejected)
    writer.writeheader()
    reject_writer.writerow(["reason", "source_row"])

    seen = set()
    rows_read = 0
    rows_written = 0
    rows_rejected = 0
    duplicates_skipped = 0

    for row in reader:
        rows_read += 1

        try:
            invoice = (row.get("InvoiceNo") or "").strip()
            stock = (row.get("StockCode") or "").strip()
            description = (row.get("Description") or "").strip()
            country = (row.get("Country") or "").strip()
            quantity = int(row["Quantity"])
            price = Decimal((row["UnitPrice"] or "").strip())
            customer = (row.get("CustomerID") or "").strip()
            date_text = (row["InvoiceDate"] or "").strip()

            # The commonly used CSV version has dates like 01-12-2010 08:26.
            invoice_date = datetime.strptime(date_text, "%d-%m-%Y %H:%M")

            if not invoice or not stock or not description:
                raise ValueError("Missing required fields")

            if quantity <= 0 or price <= 0:
                raise ValueError("Not a positive sales line")

            if invoice.upper().startswith("C"):
                raise ValueError("Cancellation invoice")

            dedupe_key = (
                invoice,
                stock,
                date_text,
                quantity,
                price,
                customer,
            )
            if dedupe_key in seen:
                duplicates_skipped += 1
                continue
            seen.add(dedupe_key)

            total_amount = price * quantity

            writer.writerow({
                "invoice_no": invoice,
                "stock_code": stock,
                "description": description,
                "quantity": quantity,
                "invoice_timestamp": invoice_date.strftime("%Y-%m-%d %H:%M:%S"),
                "unit_price": f"{price:.2f}",
                "customer_id": customer,
                "country": country,
                "total_amount": f"{total_amount:.2f}",
            })
            rows_written += 1

        except (ValueError, TypeError, KeyError, InvalidOperation) as exc:
            rows_rejected += 1
            reject_writer.writerow([
                str(exc),
                json.dumps(row, ensure_ascii=False),
            ])

    s3.put_object(
        Bucket=BUCKET,
        Key=OUTPUT_KEY,
        Body=output.getvalue().encode("utf-8"),
        ContentType="text/csv; charset=utf-8",
    )

    s3.put_object(
        Bucket=BUCKET,
        Key=REJECTED_KEY,
        Body=rejected.getvalue().encode("utf-8"),
        ContentType="text/csv; charset=utf-8",
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "rows_read": rows_read,
            "rows_written": rows_written,
            "duplicates_skipped": duplicates_skipped,
            "rows_rejected": rows_rejected,
            "output_key": OUTPUT_KEY,
            "rejected_key": REJECTED_KEY,
        }),
    }
