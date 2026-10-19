# AWS E-Commerce Sales Data Lake

An end-to-end serverless data engineering project that cleans the public **UCI Online Retail** dataset using AWS Lambda, stores raw and curated CSV files in Amazon S3, and analyzes sales with Amazon Athena.

## Architecture

```text
Public UCI Online Retail CSV
          |
          v
Amazon S3 (raw/online-retail/)
          |
          v
AWS Lambda (Python + boto3)
  - Decode source CSV (Windows-1252)
  - Validate rows and dates
  - Skip cancellations, invalid sales lines, and duplicates
  - Calculate total_amount
  - Write rejected rows separately
          |
          +--------------------+
          v                    v
S3 curated/sales/        S3 rejected/
          |
          v
Amazon Athena (external table, manually defined)
          |
          v
SQL sales analysis by country, product, and time
```

## AWS services

- **Amazon S3**: raw, curated, rejected, and Athena query-result storage.
- **AWS Lambda**: serverless CSV ETL; no AWS Glue crawler or Glue job required.
- **Amazon Athena**: SQL analytics over the curated CSV.
- **AWS IAM**: least-privilege access for Lambda and Athena.

## Repository layout

```text
aws-ecommerce-analytics-pipeline/
├── README.md
├── .gitignore
├── lambda/
│   └── ecommerce_csv_etl.py
├── athena/
│   ├── create_table.sql
│   └── analytics_queries.sql
└── docs/
    └── architecture.md
```

## Dataset

Use the public **Online Retail** dataset from the UCI Machine Learning Repository:
https://archive.ics.uci.edu/dataset/352/online+retail

Download the CSV/XLSX from UCI and upload the CSV to your own bucket. The dataset contains transactions from a UK-based online retailer. Do not commit the full dataset to this repository.

## S3 key layout

Replace the example bucket name with your own bucket if you deploy elsewhere.

- Input: `s3://YOUR_BUCKET/raw/online-retail/Online Retail.csv`
- Clean output: `s3://YOUR_BUCKET/curated/sales/online_retail_clean.csv`
- Rejected rows: `s3://YOUR_BUCKET/rejected/online_retail_rejected.csv`
- Athena query results: configure a separate prefix such as `s3://YOUR_BUCKET/athena-results/`

## Configure and deploy the Lambda

1. Create or open the Lambda function in the same AWS Region as the S3 bucket.
2. Set the runtime to a supported Python 3 version.
3. Add environment variable `BUCKET_NAME` with the exact S3 bucket name.
4. Configure the execution role to allow `s3:GetObject` on `arn:aws:s3:::YOUR_BUCKET/raw/online-retail/*` and `s3:PutObject` on the curated and rejected prefixes. Add CloudWatch Logs permissions.
5. Upload `lambda/ecommerce_csv_etl.py` as the function code.
6. Set the timeout high enough for your dataset (start with 1–3 minutes and adjust after measuring) and memory based on test results.
7. Test the function. The test event can be an empty JSON object: `{}`.

The Lambda code uses the source CSV's observed Windows-1252 encoding and the date format `DD-MM-YYYY HH:MM`. If your downloaded source file has a different format, update the decoder or date format accordingly.

## Create the Athena table

1. Open Athena in the same Region as your S3 bucket.
2. Under **Settings**, configure a query result location, e.g. `s3://YOUR_BUCKET/athena-results/`.
3. Select your database (or create one).
4. Run the SQL in [athena/create_table.sql](athena/create_table.sql), replacing `YOUR_BUCKET`.
5. Run the example queries in [athena/analytics_queries.sql](athena/analytics_queries.sql).

The table is created manually using DDL; **a Glue crawler is not required**. Athena still uses the AWS Glue Data Catalog to store table metadata.

## Data quality behavior

The ETL script:
- requires invoice number, stock code, and description;
- parses quantity, unit price, and invoice timestamp;
- rejects non-positive quantities/prices and cancellation invoice numbers beginning with `C`;
- skips duplicate transaction lines;
- calculates `total_amount = quantity × unit_price`;
- writes rejected source rows to a separate CSV.

Note: this is a portfolio ETL rule set, not accounting-grade revenue recognition. Excluding cancellations and negative quantities is a simplifying choice that should be revisited for a production model.

## Cost and safety controls

- Use the smallest practical Lambda memory and timeout after measuring execution.
- Avoid frequent test runs on the full dataset.
- Athena charges by data scanned; use `LIMIT` while exploring and prefer compressed columnar formats for larger production workloads.
- Set an AWS Budget alert and review Cost Explorer.
- Do not commit AWS credentials, account IDs, .env files, raw customer-level data, or downloaded datasets.
- Keep S3 Block Public Access enabled; do not make the bucket public.

## Validation checklist

- [ ] Lambda returns HTTP-style status code 200 and row counts.
- [ ] Curated output has a header and data rows.
- [ ] Rejected output has a header and any rejected records.
- [ ] Athena `SELECT COUNT(*) FROM ecommerce_sales;` returns a non-zero count.
- [ ] Aggregation queries return results.
- [ ] IAM policy grants only the required S3 prefixes and CloudWatch logging.

## Limitations and next steps

This project uses CSV and a single Lambda invocation to keep the deployment approachable. For larger datasets, consider chunked processing, Parquet output, partitioning by date, orchestration, automated tests, and CI/CD.

## License

The code in this repository is provided for educational and portfolio use. Refer to the UCI dataset page for dataset terms and attribution.
