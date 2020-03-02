# help message to display for faws s3
# @params
# $1: operation type

# help message
function usage() {
  local action_command="$1"
  if [[ -z "$action_command" ]]; then
    echo "usage: faws s3 [-h] {upload,download,delete,bucket,presign} ...\n"
    echo "perform CRUD operation with cp/mv/rm in s3 bucket interactively"
    echo "without positional arguments, it will only print the selected item s3 path\n"
    echo "positional arguments:"
    echo "  {upload,download,delete,bucket,presign,ls}\n"
    echo "optional arguments:"
    echo "  -h\t\tshow this help message and exit"
  elif [[ "$action_command" == 'bucket' ]]; then
    echo "usage: faws s3 bucket [-h] [-p] [-m] [-s] [-r]\n"
    echo "transfer file between buckets\n"
    echo "optional arguments:"
    echo "  -h\t\tshow this help message and exit"
    echo "  -p\t\tspecify a s3 path (bucketName/path) after this flag and skip s3 bucket/path selection"
    echo "  -m\t\tuse mv instead of cp command, like cut a file and paste in another bucket"
    echo "  -s\t\tuse sync instead of cp command, recursively copies new and updated files from one bucket to another"
    echo "  -r\t\toperate recursively, set this flag when manipulating folders"
  elif [[ "$action_command" == 'delete' ]]; then
    echo "usage: faws s3 delete [-h] [-p] [-r]\n"
    echo "delete files on a s3 bucket, to delete folder, set -r flag\n"
    echo "optional arguments:"
    echo "  -h\t\tshow this help message and exit"
    echo "  -p PATH\t\tspecify a s3 path (bucketName/path) after this flag and skip s3 bucket/path selection"
    echo "  -r\t\toperate recursively, set this flag when manipulating folders"
  elif [[ "$action_command" == 'ls' ]]; then
    echo "usage: faws s3 delete [-h]\n"
    echo "list all files in the selected bucket and get the s3 path on selection\n"
    echo "optional arguments:"
    echo "  -h\t\tshow this help message and exit"
  elif [[ "$action_command" == 'presign' ]]; then
    echo "usage: faws s3 presign [-h] [-p] [-t]\n"
    echo "generate a temprary download url for the selected s3 object"
    echo "optional arguments:\n"
    echo "  -h\t\tshow this help message and exit"
    echo "  -p PATH\tspecify a s3 path (bucketName/path) after this flag and skip s3 bucket/path selection"
    echo "  -t TIME\tspecify the expire time of the url in seconds, default is 3600s"
  elif [[ "$action_command" == 'upload' || "$action_command" == 'download' ]]; then
    echo "usage: faws s3 "$action_command" [-h] [-p] [-P] [-m] [-s] [-r] [-R] [-H]\n"
    echo "$action_command from/to a selected bucket\n"
    echo "optional arguments:\n"
    echo "  -h\t\tshow this help message and exit"
    echo "  -p PATH\tspecify a s3 path (bucketName/path) after this flag and skip s3 bucket/path selection"
    echo "         \tE.g. -p bucketname or -p bucketname/path, don't put in the s3:// prefix"
    echo "  -P PATH\tspecify a local path for operation"
    echo "  -m\t\tuse mv instead of cp command, like cut a file and paste in another location"
    echo "  -s\t\tuse sync instead of cp command, recursively copies new and updated files from one directory to another"
    echo "  -r\t\toperate recursively, set this flag when manipulating folders"
    echo "  -R\t\tsearch local file from root directory, note: very slow if no fd installed"
    echo "  -H\t\tInclude hidden folder or directory during local file search"
  fi
}
