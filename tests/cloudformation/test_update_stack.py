from fzfaws.s3.s3 import S3
from fzfaws.cloudformation.helper.paramprocessor import ParamProcessor
import os
import io
import sys
import unittest
from unittest.mock import ANY, patch
from fzfaws.cloudformation.update_stack import update_stack
from fzfaws.utils import Pyfzf, FileLoader
from fzfaws.cloudformation import Cloudformation
from pathlib import Path


class TestCloudformationUpdateStack(unittest.TestCase):
    def setUp(self):
        self.capturedOutput = io.StringIO()
        self.data_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../data/cloudformation_template.yaml",
        )
        sys.stdout = self.capturedOutput
        fileloader = FileLoader()
        config_path = Path(__file__).resolve().parent.joinpath("../data/fzfaws.yml")
        fileloader.load_config_file(config_path=str(config_path))

    def tearDown(self):
        sys.stdout = sys.__stdout__

    @patch("fzfaws.cloudformation.update_stack.ParamProcessor")
    @patch("fzfaws.cloudformation.update_stack.CloudformationArgs")
    @patch("fzfaws.cloudformation.update_stack.Cloudformation")
    def test_non_replacing_update(self, MockedCloudformation, MockedArgs, MockedParam):
        cloudformation = MockedCloudformation()
        cloudformation.stack_name = "testing1"
        cloudformation.stack_details = {
            "Parameters": [
                {"ParameterKey": "SSHLocation", "ParameterValue": "0.0.0.0/0"},
                {"ParameterKey": "Hello", "ParameterValue": "i-0a23663d658dcee1c"},
                {"ParameterKey": "WebServer", "ParameterValue": "No"},
            ],
        }
        cloudformation.set_stack.return_value = None
        cloudformation.execute_with_capabilities.return_value = {}
        with open(self.data_path, "r") as file:
            cloudformation.client.get_template.return_value = {
                "TemplateBody": file.read()
            }
        paramprocessor = MockedParam()
        paramprocessor.process_stack_params.return_value = None
        paramprocessor.processed_params = [
            {"ParameterKey": "SSHLocation", "ParameterValue": "0.0.0.0/0"},
            {"ParameterKey": "Hello", "ParameterValue": "i-0a23663d658dcee1c"},
            {"ParameterKey": "WebServer", "ParameterValue": "Yes"},
        ]

        update_stack()

        cloudformation.execute_with_capabilities.assert_called_with(
            Parameters=[
                {"ParameterKey": "SSHLocation", "ParameterValue": "0.0.0.0/0"},
                {"ParameterKey": "Hello", "ParameterValue": "i-0a23663d658dcee1c"},
                {"ParameterKey": "WebServer", "ParameterValue": "Yes"},
            ],
            StackName="testing1",
            UsePreviousTemplate=True,
            cloudformation_action=ANY,
        )

        # extra args
        cloudformation.wait.return_value = None
        args = MockedArgs()
        args.set_extra_args.return_value = None
        args.extra_args = {"foo": "boo"}
        update_stack(wait=True, extra=True, profile=True, region="us-east-1")
        MockedCloudformation.assert_called_with(True, "us-east-1")
        cloudformation.wait.assert_called_with(
            "stack_update_complete", "Wating for stack to be updated ..."
        )
        cloudformation.execute_with_capabilities.assert_called_with(
            Parameters=[
                {"ParameterKey": "SSHLocation", "ParameterValue": "0.0.0.0/0"},
                {"ParameterKey": "Hello", "ParameterValue": "i-0a23663d658dcee1c"},
                {"ParameterKey": "WebServer", "ParameterValue": "Yes"},
            ],
            StackName="testing1",
            UsePreviousTemplate=True,
            cloudformation_action=ANY,
            foo="boo",
        )
        args.set_extra_args.assert_called_with(
            update=True, search_from_root=False, dryrun=False
        )

    @patch("fzfaws.cloudformation.update_stack.ParamProcessor")
    @patch("fzfaws.cloudformation.update_stack.Cloudformation")
    def test_dryrun(self, MockedCloudformation, MockedParam):
        cloudformation = MockedCloudformation()
        cloudformation.stack_name = "testing1"
        cloudformation.stack_details = {
            "Parameters": [
                {"ParameterKey": "SSHLocation", "ParameterValue": "0.0.0.0/0"},
                {"ParameterKey": "Hello", "ParameterValue": "i-0a23663d658dcee1c"},
                {"ParameterKey": "WebServer", "ParameterValue": "No"},
            ],
        }
        cloudformation.set_stack.return_value = None
        cloudformation.execute_with_capabilities.return_value = {}
        cloudformation.execute_with_capabilities.return_value = {}
        with open(self.data_path, "r") as file:
            cloudformation.client.get_template.return_value = {
                "TemplateBody": file.read()
            }
        paramprocessor = MockedParam()
        paramprocessor.process_stack_params.return_value = None
        paramprocessor.processed_params = [
            {"ParameterKey": "SSHLocation", "ParameterValue": "0.0.0.0/0"},
            {"ParameterKey": "Hello", "ParameterValue": "i-0a23663d658dcee1c"},
            {"ParameterKey": "WebServer", "ParameterValue": "Yes"},
        ]

        result = update_stack(dryrun=True)
        self.assertEqual(
            result,
            {
                "Parameters": [
                    {"ParameterKey": "SSHLocation", "ParameterValue": "0.0.0.0/0"},
                    {"ParameterKey": "Hello", "ParameterValue": "i-0a23663d658dcee1c"},
                    {"ParameterKey": "WebServer", "ParameterValue": "Yes"},
                ],
                "StackName": "testing1",
                "UsePreviousTemplate": True,
                "cloudformation_action": ANY,
            },
        )

    @patch("fzfaws.cloudformation.update_stack.validate_stack")
    @patch.object(Cloudformation, "execute_with_capabilities")
    @patch.object(ParamProcessor, "process_stack_params")
    @patch.object(Pyfzf, "get_local_file")
    @patch.object(Cloudformation, "set_stack")
    def test_local_replacing_update(
        self, mocked_stack, mocked_local, mocked_param, mocked_execute, mocked_validate
    ):
        mocked_local.return_value = self.data_path
        update_stack(local_path=True, root=True, replace=True)
        mocked_local.assert_called_with(search_from_root=True, cloudformation=True)
        mocked_param.assert_called_once()
        mocked_execute.assert_called_with(
            Parameters=[],
            StackName="",
            TemplateBody=ANY,
            cloudformation_action=ANY,
            UsePreviousTemplate=False,
        )
        mocked_validate.assert_called_with(
            "default", "us-east-1", local_path=self.data_path, no_print=True
        )

        mocked_local.reset_mock()
        mocked_param.reset_mock()
        update_stack(local_path=self.data_path, replace=True)
        mocked_local.assert_not_called()
        mocked_param.assert_called_once()
        mocked_execute.assert_called_with(
            Parameters=[],
            StackName="",
            TemplateBody=ANY,
            cloudformation_action=ANY,
            UsePreviousTemplate=False,
        )
        mocked_validate.assert_called_with(
            "default", "us-east-1", local_path=self.data_path, no_print=True
        )

    @patch.object(Cloudformation, "execute_with_capabilities")
    @patch.object(S3, "get_object_url")
    @patch.object(ParamProcessor, "process_stack_params")
    @patch.object(S3, "get_object_data")
    @patch("fzfaws.cloudformation.update_stack.validate_stack")
    @patch.object(S3, "get_object_version")
    @patch.object(Cloudformation, "set_stack")
    def test_s3_replacing_update(
        self,
        mocked_stack,
        mocked_version,
        mocked_validate,
        mocked_data,
        mocked_process,
        mocked_url,
        mocked_execute,
    ):
        fileloader = FileLoader(self.data_path)
        mocked_data.return_value = fileloader.process_yaml_file()
        mocked_version.return_value = [{"VersionId": "111111"}]
        mocked_url.return_value = "https://s3-ap-southeast-2.amazonaws.com/kazhala-lol/hello.yaml?versionId=111111"
        update_stack(replace=True, bucket="kazhala-lol/hello.yaml", version=True)
        mocked_version.assert_called_with("kazhala-lol", "hello.yaml")
        mocked_validate.assert_called_with(
            "default",
            "us-east-1",
            bucket="kazhala-lol/hello.yaml",
            version="111111",
            no_print=True,
        )
        mocked_execute.assert_called_with(
            Parameters=[],
            StackName="",
            TemplateURL="https://s3-ap-southeast-2.amazonaws.com/kazhala-lol/hello.yaml?versionId=111111",
            UsePreviousTemplate=False,
            cloudformation_action=ANY,
        )

        mocked_version.reset_mock()
        update_stack(replace=True, bucket="kazhala-lol/hello.yaml", version="111111")
        mocked_version.assert_not_called()
        mocked_validate.assert_called_with(
            "default",
            "us-east-1",
            bucket="kazhala-lol/hello.yaml",
            version="111111",
            no_print=True,
        )
        mocked_execute.assert_called_with(
            Parameters=[],
            StackName="",
            TemplateURL="https://s3-ap-southeast-2.amazonaws.com/kazhala-lol/hello.yaml?versionId=111111",
            UsePreviousTemplate=False,
            cloudformation_action=ANY,
        )
