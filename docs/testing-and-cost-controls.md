# Testing and Cost Controls

## Lambda test checklist

1. Verify that `BUCKET_NAME` is set in Lambda environment variables.
2. Verify that the input object exists at `raw/online-retail/Online Retail.csv`.
3. Confirm that the CSV header names match the code's expected columns.
4. Confirm the date format. The current parser expects `DD-MM-YYYY HH:MM`.
5. Invoke the Lambda function manually.
6. Inspect the JSON response:
   - `rows_read`
   - `rows_written`
   - `duplicates_skipped`
   - `rows_rejected`
7. Download the curated file and verify it contains a header and data rows.
8. Check the rejected file for invalid rows and reasons.
9. Review the Lambda log group in CloudWatch.

## Athena checks

After creating the table, run:

```sql
SELECT COUNT(*) FROM ecommerce_sales;
SELECT * FROM ecommerce_sales LIMIT 10;
```

If the count is zero:
- Confirm the Lambda output file has data, not just a header.
- Confirm the table's S3 LOCATION points to the exact curated prefix.
- Confirm the table schema and CSV header count setting are correct.
- Confirm the Lambda role wrote to the same bucket and Region you are querying.

Athena query results are separate from the query's name. Athena stores result files under the configured query-result S3 location, often in generated folders and filenames.

## Security

- Never commit AWS access keys, secret keys, session tokens, account-specific secrets, or local AWS credential files.
- Prefer an IAM role with least-privilege access.
- Do not make the source bucket public.
- The source dataset may contain customer identifiers. Keep raw row-level data out of the public Git repository.

## Cost controls

- Configure an AWS Budget alert.
- Athena is billed by data scanned; avoid `SELECT *` on large datasets and consider Parquet for future improvements.
- Keep test inputs small while debugging.
- Set CloudWatch log retention to a limited period.
- Remove unused S3 objects and resources when the project is complete.
- Review current AWS pricing and Free Tier terms for your Region before running the project.
