from argparse import ArgumentParser
import boto3

parser = ArgumentParser()
parser.add_argument('--bucket', type=str, default='tanks.hex7.com', help='s3 bucket')
args = parser.parse_args()
filenames = [ 'index.html', 'gemini.html', 'claude.html' ]

print('uploading: ', args.bucket, filenames)

extra_args = {'ACL': 'public-read',
              'ContentType': 'text/html',
              'ContentLanguage': 'en-US'}

s3_client = boto3.client('s3')
for f in filenames:
  try:
    s3_client.upload_file(Filename=f,
                          Key=f,
                          Bucket=args.bucket,
                          ExtraArgs=extra_args)
  except:
    raise Exception('cannot write file to s3: ' + f)

print('SUCCESS: ', args.bucket, filenames)
