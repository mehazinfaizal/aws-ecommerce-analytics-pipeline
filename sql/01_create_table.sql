-- Select your Athena database before running this statement.
-- Replace YOUR_BUCKET_NAME with the actual S3 bucket name.
-- The table reads the curated CSV written by Lambda; no Glue crawler is needed.

CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_sales (
    invoice_no         string,
    stock_code         string,
    description        string,
    quantity           int,
    invoice_timestamp  timestamp,
    unit_price         decimal(12,2),
    customer_id        string,
    country            string,
    total_amount       decimal(14,2)
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    'separatorChar' = ',',
    'quoteChar' = '"',
    'escapeChar' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://YOUR_BUCKET_NAME/curated/sales/'
TBLPROPERTIES ('skip.header.line.count'='1');
