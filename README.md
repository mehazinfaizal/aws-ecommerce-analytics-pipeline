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
  - Decode source CSV
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

## Data quality behavior

The ETL script:
- requires invoice number, stock code, and description;
- parses quantity, unit price, and invoice timestamp;
- rejects non-positive quantities/prices and cancellation invoice numbers beginning with `C`;
- skips duplicate transaction lines;
- calculates `total_amount = quantity × unit_price`;
- writes rejected source rows to a separate CSV.

## Limitations and next steps

This project uses CSV and a single Lambda invocation to keep the deployment approachable. For larger datasets, consider chunked processing, Parquet output, partitioning by date, orchestration, automated tests, and CI/CD.

