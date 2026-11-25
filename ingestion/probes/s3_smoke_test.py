import os
import boto3
from dotenv import load_dotenv

load_dotenv()
profile = os.environ["AWS_PROFILE"]
bucket = os.environ["S3_BUCKET"]

s3 = boto3.Session(profile_name=profile).client("s3")

key = "raw/_smoke_test/hola.txt"
s3.put_object(Bucket=bucket, Key=key, Body="hola desde python".encode("utf-8"))
print(f"Subido: s3://{bucket}/{key}")

resp = s3.list_objects_v2(Bucket=bucket, Prefix="raw/")
for obj in resp.get("Contents", []):
    print(" -", obj["Key"], obj["Size"], "bytes")