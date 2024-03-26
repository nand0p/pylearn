from argparse import ArgumentParser
import boto3

parser = ArgumentParser()
parser.add_argument('--filename', type=str, default='index.html', help='out directory')
parser.add_argument('--bucket', type=str, default='tanks.hex7.com', help='s3 bucket')
args = parser.parse_args()

print('uploading: ', args.bucket, args.filename)

extra_args = {'ACL': 'public-read',
              'ContentType': 'text/html',
              'ContentLanguage': 'en-US'}

s3_client = boto3.client('s3')
try:
  s3_client.upload_file(Filename=args.filename,
                        Bucket=args.bucket,
                        Key=args.filename,
                        ExtraArgs=extra_args)
except:
  raise Exception('cannot write to s3')

print('SUCCESS: ', args.bucket, args.filename)
