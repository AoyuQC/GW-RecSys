#!/usr/bin/env python3

from aws_cdk import core

# from deploy.gw_stack import GWStack
from deploy.gw_graph_stack import GWGraphStack
# from deploy.gw_trainhandler_stack import GWTrainHandlerStack


app = core.App()
# GWStack(app, "gw-recommendation-stack")
GWGraphStack(app, "gw-graph-stack")
# GWTrainHandlerStack(app, "gw-train-stack")

app.synth()
