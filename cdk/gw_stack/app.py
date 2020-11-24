#!/usr/bin/env python3

from aws_cdk import core

from deploy.gw_stack import GWStack


app = core.App()
GWStack(app, "gw-recommendation-stack")

app.synth()
