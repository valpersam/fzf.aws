import io
import sys
import unittest
from unittest.mock import call, patch
from fzfaws.s3.bucket_s3 import bucket_s3
from fzfaws.s3 import S3


class TestS3BucketCopy(unittest.TestCase):
    def setUp(self):
        self.capturedOutput = io.StringIO()
        sys.stdout = self.capturedOutput

    def tearDown(self):
        sys.stdout = sys.__stdout__

    @patch.object(S3, "set_s3_bucket")
    @patch.object(S3, "get_object_version")
    @patch.object(S3, "set_s3_object")
    @patch.object(S3, "set_s3_path")
    @patch("fzfaws.s3.bucket_s3.sync_s3")
    def test_sync(
        self, mocked_sync, mocked_path, mocked_object, mocked_version, mocked_bucket
    ):
        bucket_s3(sync=True, exclude=["*"], include=["hello*"])
        mocked_object.assert_not_called()
        mocked_version.assert_not_called()
        mocked_bucket.assert_has_calls(
            [
                call(
                    header="Set the source bucket which contains the file to transfer"
                ),
                call(
                    header="Set the destination bucket where the file should be transfered"
                ),
            ]
        )
        mocked_sync.assert_called_with(["*"], ["hello*"], "s3:///", "s3:///")

        bucket_s3(
            sync=True,
            exclude=["*"],
            include=["hello*"],
            from_bucket="kazhala-lol/",
            to_bucket="kazhala-yes/foo/",
            version=True,
        )
        mocked_version.assert_not_called()
        mocked_object.assert_not_called()
        mocked_sync.assert_called_with(
            ["*"], ["hello*"], "s3://kazhala-lol/", "s3://kazhala-yes/foo/"
        )

    @patch.object(S3, "set_s3_path")
    @patch.object(S3, "set_s3_bucket")
    @patch.object(S3, "get_object_version")
    @patch("fzfaws.s3.bucket_s3.walk_s3_folder")
    @patch("fzfaws.s3.bucket_s3.get_confirmation")
    def test_recusive(
        self, mocked_confirm, mocked_walk, mocked_version, mocked_bucket, mocked_path
    ):
        self.capturedOutput.truncate(0)
        self.capturedOutput.seek(0)
        mocked_confirm.return_value = False
        mocked_walk.side_effect = lambda a, b, c, d, e, g, h, i, j, k: print(
            b, c, d, e, g, h, i, j, k
        )
        bucket_s3(
            recursive=True,
            from_bucket="kazhala-lol/hello/",
            to_bucket="kazhala-yes/foo/",
            exclude=["*"],
            include=["foo*"],
            version=True,
        )
        self.assertEqual(
            self.capturedOutput.getvalue(),
            "kazhala-lol hello/ hello/ [] ['*'] ['foo*'] bucket foo/ kazhala-yes\n",
        )
        mocked_version.assert_not_called()

        self.capturedOutput.truncate(0)
        self.capturedOutput.seek(0)
        bucket_s3(recursive=True)
        self.assertEqual(
            self.capturedOutput.getvalue(), "   [] [] [] bucket  \n",
        )
        mocked_bucket.assert_has_calls(
            [
                call(
                    header="Set the source bucket which contains the file to transfer"
                ),
                call(
                    header="Set the destination bucket where the file should be transfered"
                ),
            ]
        )
        mocked_path.assert_has_calls([call(), call()])

    @patch.object(S3, "set_s3_path")
    @patch.object(S3, "set_s3_object")
    @patch.object(S3, "set_s3_bucket")
    @patch.object(S3, "get_object_version")
    @patch("fzfaws.s3.bucket_s3.get_confirmation")
    def test_version(
        self, mocked_confirm, mocked_version, mocked_bucket, mocked_obj, mocked_path
    ):
        mocked_confirm.return_value = False
        mocked_version.return_value = [{"Key": "hello.txt", "VersionId": "11111111"}]

        self.capturedOutput.truncate(0)
        self.capturedOutput.seek(0)
        bucket_s3(
            from_bucket="kazhala-lol/hello.txt",
            to_bucket="kazhala-yes/foo/",
            version=True,
        )
        self.assertEqual(
            self.capturedOutput.getvalue(),
            "(dryrun) copy: s3://kazhala-lol/hello.txt to s3://kazhala-yes/foo/hello.txt with version 11111111\n",
        )

        self.capturedOutput.truncate(0)
        self.capturedOutput.seek(0)
        mocked_version.return_value = [{"Key": "hello.txt", "VersionId": "11111111"}]
        bucket_s3(version=True)
        self.assertEqual(
            self.capturedOutput.getvalue(),
            "(dryrun) copy: s3:///hello.txt to s3:///hello.txt with version 11111111\n",
        )
        mocked_bucket.assert_has_calls(
            [
                call(
                    header="Set the source bucket which contains the file to transfer"
                ),
                call(
                    header="Set the destination bucket where the file should be transfered"
                ),
            ]
        )
        mocked_obj.assert_has_calls([call(multi_select=True, version=True)])
        mocked_path.assert_called_once()