"""handles uploading operation of s3

upload local files/directories to s3
"""
import json
import os
from fzfaws.s3.s3 import S3
from fzfaws.utils.exceptions import InvalidS3PathPattern
from fzfaws.utils.pyfzf import Pyfzf
from fzfaws.utils.util import get_confirmation


def upload_s3(args):
    """upload local files/directories to s3

    upload through boto3 s3 client

    Args:
        args: argparse args
    Returns:
        None
    Exceptions:
        InvalidS3PathPattern: when the -p flag specifed s3 path is invalid pattern
    """

    s3 = S3()
    if args.path:
        try:
            if s3.validate_input_path(args.path[0]):
                s3.bucket_name = args.path[0].split('/')[0]
                s3.bucket_path = '/'.join(args.path[0].split('/')[1:])
            else:
                raise InvalidS3PathPattern
        except InvalidS3PathPattern:
            print(
                'Invalid s3 path pattern, valid pattern(Bucket/ or Bucket/path/to/upload)')
            exit()
    else:
        s3.set_s3_bucket()
        s3.set_s3_path()

    fzf = Pyfzf()
    if args.local:
        local_path = args.local[0]
    else:
        local_path = fzf.get_local_file(args.root, directory=args.recursive)

    if args.recursive:
        upload_list = []
        for root, dirs, files in os.walk(local_path):
            for filename in files:
                full_path = os.path.join(root, filename)
                relative_path = os.path.relpath(full_path, local_path)
                destination_key = s3.get_s3_destination_key(
                    relative_path, recursive=True)
                print('(dryrung) upload: %s to s3://%s/%s' %
                      (relative_path, s3.bucket_name, destination_key))
                upload_list.append(
                    {'local': full_path, 'bucket': s3.bucket_name, 'key': destination_key, 'relative': relative_path})

        if get_confirmation('Confirm?'):
            for item in upload_list:
                print('Uploading %s' % item['relative'])
                s3.client.upload_file(
                    item['local'], item['bucket'], item['key'])

    else:
        # get the formated s3 destination
        destination_key = s3.get_s3_destination_key(local_path)
        print('%s will be uploaded to %s/%s' %
              (local_path, s3.bucket_name, destination_key))

        if get_confirmation('Confirm?'):
            response = s3.client.upload_file(
                local_path, s3.bucket_name, destination_key)
            print('File uploaded')
