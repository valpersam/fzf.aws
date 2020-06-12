"""sync operation handler

handles bucket/upload/download sync operation
"""
import subprocess
from fzfaws.utils import get_confirmation
from typing import Optional, List
from fzfaws.utils.exceptions import InvalidS3PathPattern


def sync_s3(
    exclude: Optional[List[str]] = None,
    include: Optional[List[str]] = None,
    from_path: str = "",
    to_path: str = "",
) -> None:
    """sync from_path with to_path

    utilizing subprocess to call aws cli s3 sync, as boto3 doesn't provide
    way to have sync operation.

    May try to implement the sync myself using S3 ETag calculation to compare
    file, require more time and benchmark to see time difference

    For now, sync is the only process require aws cli to be installed

    :param exclude: list of files to exclude
    :type exclude: List[str], Optional
    :param include: list of files to explicit include
    :type include: List[str], Optional
    :param from_path: orignal file location
    :type from_path: str
    :param to_path: destination file location
    :type to_path: str
    """

    if not from_path or not to_path:
        raise InvalidS3PathPattern(
            "Invalid S3 path pattern for sync, example: s3://bucketname/path/"
        )

    if not exclude:
        exclude = []
    if not include:
        include = []
    # add in the exclude flag and include flag into the command list
    exclude_list: List[str] = []
    include_list: List[str] = []
    for pattern in exclude:
        if not exclude_list:
            exclude_list.append("--exclude")
        exclude_list.append(pattern)
    for pattern in include:
        if not include_list:
            include_list.append("--include")
        include_list.append(pattern)

    cmd_list: List[str] = ["aws", "s3", "sync", from_path, to_path]
    cmd_list.extend(exclude_list)
    cmd_list.extend(include_list)
    cmd_list.append("--dryrun")

    sync_dry = subprocess.Popen(cmd_list)
    sync_dry.communicate()
    if get_confirmation("Confirm?"):
        # remove the dryrun flag and actually invoke it
        cmd_list.pop()
        sync = subprocess.Popen(cmd_list)
        sync.communicate()
        print("%s synced with %s" % (from_path, to_path))
