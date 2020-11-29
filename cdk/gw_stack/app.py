#!/usr/bin/env python3

from aws_cdk import core

# from deploy.gw_stack import GWStack
from deploy.gw_graph_stack import GWGraphStack


app = core.App()
# GWStack(app, "gw-recommendation-stack")
GWGraphStack(app, "gw-graph-stack")

app.synth()
