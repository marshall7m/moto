from __future__ import unicode_literals

import unittest
import json

from moto.awslambda.policy import Policy


class MockLambdaFunction:
    def __init__(self, arn):
        self.function_arn = arn
        self.policy = None


class TestPolicy(unittest.TestCase):
    def test_policy(self):
        policy = Policy(MockLambdaFunction("arn"))
        statement = {
            "StatementId": "statement0",
            "Action": "lambda:InvokeFunction",
            "FunctionName": "function_name",
            "Principal": "events.amazonaws.com",
            "SourceArn": "arn:aws:events:us-east-1:111111111111:rule/rule_name",
            "SourceAccount": "111111111111",
        }

        expected = {
            "Action": "lambda:InvokeFunction",
            "FunctionName": "function_name",
            "Principal": {"Service": "events.amazonaws.com"},
            "Effect": "Allow",
            "Resource": "arn:$LATEST",
            "Sid": "statement0",
            "Condition": {
                "ArnLike": {
                    "AWS:SourceArn": "arn:aws:events:us-east-1:111111111111:rule/rule_name",
                },
                "StringEquals": {"AWS:SourceAccount": "111111111111"},
            },
        }

        policy.add_statement(json.dumps(statement))
        self.assertDictEqual(expected, policy.statements[0])

        sid = statement.get("StatementId", None)
        if sid == None:
            raise "TestCase.statement does not contain StatementId"

        policy.del_statement(sid)
        self.assertEqual([], policy.statements)
