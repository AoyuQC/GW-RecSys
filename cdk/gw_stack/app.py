#!/usr/bin/env python3

from aws_cdk import core

# from deploy.gw_stack import GWStack
from deploy.gw_graph_stack import GWGraphStack
from deploy.gw_infra_stack import CdkInfraStack
from deploy.gw_dkn_stack import GWDknStack
from deploy.gw_inferhandler_stack import GWInferHandlerStack
from deploy.gw_sample_stack import GWSampleStack

# from deploy.gw_trainhandler_stack import GWTrainHandlerStack



app = core.App()
# GWStack(app, "gw-recommendation-stack")
#GWGraphStack(app, "gw-graph-stack")
#GWInferHandlerStack(app, "gw-inferhandler-stack")

#GWGraphStack(app, "gw-graph-stack")
# GWTrainHandlerStack(app, "gw-train-stack")

infra_stack = CdkInfraStack(app, "cdk-stack-infer-infra")

sample_stack = GWSampleStack(app, "cdk-stack-infer-Sample", infra_stack.vpc)
#graph_stack = GWGraphStack(app, "cdk-stack-infer-graph", infra_stack.vpc)
#dkn_stack = GWDknStack(app, "cdk-stack-infer-dkn", infra_stack.vpc)
"""
infer_handler_stack = GWInferHandlerStack(
    app, 
    "cdk-stack-infer-handler", 
    infra_stack.vpc, 
    graph_stack.graph_inference_dns, 
    dkn_stack.url
)
"""
app.synth()
