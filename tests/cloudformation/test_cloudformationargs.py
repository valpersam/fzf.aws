from fzfaws.iam.iam import IAM
import io
import json
import os
import sys
import unittest
from unittest.mock import call, patch

from fzfaws.cloudformation import Cloudformation
from fzfaws.cloudformation.helper.cloudformationargs import CloudformationArgs
from fzfaws.cloudwatch import Cloudwatch
from fzfaws.sns.sns import SNS
from fzfaws.utils import Pyfzf


class TestCloudformationArgs(unittest.TestCase):
    def setUp(self):
        self.capturedOutput = io.StringIO()
        sys.stdout = self.capturedOutput
        cloudformation = Cloudformation()
        self.cloudformationargs = CloudformationArgs(cloudformation)

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_constructor(self):
        self.assertEqual(self.cloudformationargs._extra_args, {})
        self.assertEqual(self.cloudformationargs.update_termination, False)
        self.assertIsInstance(self.cloudformationargs.cloudformation, Cloudformation)

    @patch.object(Pyfzf, "execute_fzf")
    @patch.object(Pyfzf, "append_fzf")
    @patch.object(CloudformationArgs, "set_creation")
    @patch.object(CloudformationArgs, "set_rollback")
    @patch.object(CloudformationArgs, "set_notification")
    @patch.object(CloudformationArgs, "set_policy")
    @patch.object(CloudformationArgs, "set_permissions")
    @patch.object(CloudformationArgs, "set_tags")
    def test_set_extra_args(
        self,
        mocked_tags,
        mocked_perm,
        mocked_policy,
        mocked_notify,
        mocked_rollback,
        mocked_create,
        mocked_append,
        mocked_execute,
    ):
        # normal test
        mocked_execute.return_value = [
            "Tags",
            "Permissions",
            "StackPolicy",
            "Notifications",
            "RollbackConfiguration",
            "CreationOption",
        ]
        self.cloudformationargs.set_extra_args()
        mocked_tags.assert_called_once_with(False)
        mocked_perm.assert_called_once_with(False)
        mocked_notify.assert_called_once_with(False)
        mocked_rollback.assert_called_once_with(False)
        mocked_policy.assert_called_once_with(False, False)
        mocked_create.assert_called_once_with(False)
        mocked_append.assert_has_calls(
            [
                call("Tags\n"),
                call("Permissions\n"),
                call("StackPolicy\n"),
                call("Notifications\n"),
                call("RollbackConfiguration\n"),
                call("CreationOption\n"),
            ]
        )

        mocked_tags.reset_mock()
        mocked_perm.reset_mock()
        mocked_notify.reset_mock()
        mocked_rollback.reset_mock()
        mocked_policy.reset_mock()
        mocked_create.reset_mock()
        mocked_append.reset_mock()
        # update test
        self.cloudformationargs.set_extra_args(update=True, search_from_root=True)
        mocked_tags.assert_called_once_with(True)
        mocked_perm.assert_called_once_with(True)
        mocked_notify.assert_called_once_with(True)
        mocked_rollback.assert_called_once_with(True)
        mocked_policy.assert_called_once_with(True, True)
        mocked_create.assert_called_once_with(True)
        mocked_append.assert_has_calls(
            [
                call("Tags\n"),
                call("Permissions\n"),
                call("StackPolicy\n"),
                call("Notifications\n"),
                call("RollbackConfiguration\n"),
                call("UpdateOption\n"),
            ]
        )

        mocked_tags.reset_mock()
        mocked_perm.reset_mock()
        mocked_notify.reset_mock()
        mocked_rollback.reset_mock()
        mocked_policy.reset_mock()
        mocked_create.reset_mock()
        mocked_append.reset_mock()
        # dryrun test
        self.cloudformationargs.set_extra_args(dryrun=True)
        mocked_tags.assert_called_once_with(False)
        mocked_perm.assert_called_once_with(False)
        mocked_notify.assert_called_once_with(False)
        mocked_rollback.assert_called_once_with(False)
        mocked_policy.assert_called_once_with(False, False)
        mocked_create.assert_called_once_with(False)
        mocked_append.assert_has_calls(
            [
                call("Tags\n"),
                call("Permissions\n"),
                call("Notifications\n"),
                call("RollbackConfiguration\n"),
            ]
        )

    @patch("builtins.input")
    @patch.object(Pyfzf, "execute_fzf")
    @patch.object(Pyfzf, "append_fzf")
    def test_set_creation(self, mocked_append, mocked_execute, mocked_input):
        self.cloudformationargs._extra_args = {}

        # normal test
        mocked_execute.return_value = [
            "RollbackOnFailure",
            "TimeoutInMinutes",
            "EnableTerminationProtection",
        ]
        mocked_input.return_value = 1
        self.cloudformationargs.set_creation()
        mocked_append.assert_has_calls(
            [
                call("RollbackOnFailure\n"),
                call("TimeoutInMinutes\n"),
                call("EnableTerminationProtection\n"),
                call("True\n"),
                call("False\n"),
                call("True\n"),
                call("False\n"),
            ]
        )
        mocked_execute.assert_has_calls(
            [
                call(
                    empty_allow=True,
                    print_col=1,
                    multi_select=True,
                    header="select options to configure",
                ),
                call(
                    empty_allow=True,
                    print_col=1,
                    header="Roll back on failue? (Default: True)",
                ),
                call(
                    empty_allow=True,
                    print_col=1,
                    header="%sEnable termination protection? (Default: False)",
                ),
            ]
        )
        self.assertEqual(
            self.cloudformationargs.extra_args,
            {
                "OnFailure": "DO_NOTHING",
                "TimeoutInMinutes": 1,
                "EnableTerminationProtection": False,
            },
        )

        # update test
        self.cloudformationargs._extra_args = {}
        mocked_append.reset_mock()
        mocked_execute.reset_mock()
        mocked_input.reset_mock()
        mocked_execute.return_value = [
            "EnableTerminationProtection",
        ]
        mocked_input.return_value = 1
        self.cloudformationargs.set_creation(update=True)
        mocked_append.assert_has_calls(
            [call("EnableTerminationProtection\n"), call("True\n"), call("False\n"),]
        )
        mocked_execute.assert_has_calls(
            [
                call(
                    empty_allow=True,
                    print_col=1,
                    multi_select=True,
                    header="select options to configure",
                ),
                call(
                    empty_allow=True,
                    print_col=1,
                    header="Enable termination protection?",
                ),
            ]
        )
        self.assertEqual(
            self.cloudformationargs.extra_args, {},
        )
        self.assertEqual(self.cloudformationargs.update_termination, False)

    @patch("builtins.input")
    @patch.object(Cloudwatch, "set_arns")
    def test_set_rollback(self, mocked_arn, mocked_input):

        self.capturedOutput.truncate(0)
        self.capturedOutput.seek(0)
        # normal test
        self.cloudformationargs.set_rollback(update=False)
        self.assertEqual(
            self.capturedOutput.getvalue(),
            "--------------------------------------------------------------------------------\nSelected arns: ['']\n",
        )
        mocked_arn.assert_called_once_with(
            empty_allow=True,
            header="select a cloudwatch alarm to monitor the stack",
            multi_select=True,
        )
        mocked_input.assert_called_once_with("MonitoringTimeInMinutes(Default: 0): ")

        mocked_arn.reset_mock()
        mocked_input.reset_mock()
        self.capturedOutput.truncate(0)
        self.capturedOutput.seek(0)
        # update test
        self.cloudformationargs.cloudformation.stack_details = {
            "RollbackConfiguration": {
                "RollbackTriggers": "111111",
                "MonitoringTimeInMinutes": 1,
            }
        }
        self.cloudformationargs.set_rollback(update=True)
        self.assertEqual(
            self.capturedOutput.getvalue(),
            "--------------------------------------------------------------------------------\nSelected arns: ['']\n",
        )
        mocked_arn.assert_called_once_with(
            empty_allow=True,
            header="select a cloudwatch alarm to monitor the stack\nOriginal value: 111111",
            multi_select=True,
        )
        mocked_input.assert_called_once_with("MonitoringTimeInMinutes(Original: 1): ")

    @patch.object(SNS, "set_arns")
    def test_set_notification(self, mocked_arn):
        self.cloudformationargs.set_notification()
        mocked_arn.assert_called_once_with(
            empty_allow=True, header="select sns topic to notify", multi_select=True
        )

        mocked_arn.reset_mock()
        self.cloudformationargs.cloudformation.stack_details = {
            "NotificationARNs": "111111"
        }
        self.cloudformationargs.set_notification(update=True)
        mocked_arn.assert_called_once_with(
            empty_allow=True,
            header="select sns topic to notify\nOriginal value: 111111",
            multi_select=True,
        )

    @patch.object(Pyfzf, "get_local_file")
    def test_set_policy(self, mocked_file):
        mocked_file.return_value = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/policy.json"
        )
        self.cloudformationargs.set_policy()
        self.assertEqual(
            self.cloudformationargs._extra_args["StackPolicyBody"],
            json.dumps(
                {
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": "Update:*",
                            "Principal": "*",
                            "Resource": "*",
                        }
                    ]
                },
                indent=2,
            )
            + "\n",
        )
        mocked_file.assert_called_once_with(
            search_from_root=False,
            cloudformation=True,
            empty_allow=True,
            header="select the policy document you would like to use",
        )

        mocked_file.reset_mock()
        self.cloudformationargs._extra_args = {}
        self.cloudformationargs.set_policy(search_from_root=True, update=True)
        self.assertEqual(
            self.cloudformationargs._extra_args["StackPolicyDuringUpdateBody"],
            json.dumps(
                {
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": "Update:*",
                            "Principal": "*",
                            "Resource": "*",
                        }
                    ]
                },
                indent=2,
            )
            + "\n",
        )
        mocked_file.assert_called_once_with(
            search_from_root=True,
            cloudformation=True,
            empty_allow=True,
            header="select the policy document you would like to use",
        )

    @patch.object(IAM, "set_arns")
    def test_set_permissions(self, mocked_arn):
        self.cloudformationargs.set_permissions()
        mocked_arn.assert_called_once_with(
            header="Choose an IAM role to explicitly define CloudFormation's permissions\nNote: only IAM role can be assumed by CloudFormation is listed",
            service="cloudformation.amazonaws.com",
        )

        mocked_arn.reset_mock()
        self.cloudformationargs.cloudformation.stack_details = {"RoleARN": "111111"}
        self.cloudformationargs.set_permissions(update=True)
        mocked_arn.assert_called_once_with(
            header="Select a role Choose an IAM role to explicitly define CloudFormation's permissions\nOriginal value: 111111",
            service="cloudformation.amazonaws.com",
        )

    @patch("builtins.input")
    def test_set_tags(self, mocked_input):
        self.cloudformationargs._extra_args = {}
        mocked_input.return_value = ""
        self.cloudformationargs.set_tags()
        mocked_input.assert_has_calls(
            [call("TagName: "),]
        )
        self.assertEqual(self.cloudformationargs._extra_args, {})

        mocked_input.reset_mock()
        mocked_input.return_value = ""
        self.cloudformationargs.cloudformation.stack_details = {
            "Tags": [{"Key": "foo", "Value": "boo"}]
        }
        self.cloudformationargs.set_tags(update=True)
        mocked_input.assert_has_calls([call("Key(foo): "), call("Value(boo): ")])
        self.assertEqual(
            self.cloudformationargs._extra_args,
            {"Tags": [{"Key": "foo", "Value": "boo"}]},
        )