config = {}

config["job_level"] = {
    "sagemaker_role": "AirflowInstanceRole",
    "region_name": "<region-name>",  # replace
    "run_hyperparameter_opt": "no"
}

config["train_dkn"] = {
    "estimator_config": {
        "train_instance_count": 1,
        "train_instance_type": 'ml.p3.2xlarge',
        "output_path": "s3://<s3-bucket>/dkn_model/",  # replace
        "base_job_name": "dkn",
        "hyperparameters": {
            'learning_rate': 0.0001,
            'servable_model_dir': '/opt/ml/model',
            'loss_weight': 1.0,
            'use_context': True,
            'max_click_history': 30,
            'num_epochs': 1,
            'max_title_length': 16,
            'entity_dim': 128,
            'word_dim': 300,
            'batch_size': 128,
            'perform_shuffle': 1,
            'checkpointPath': '/opt/ml/checkpoints'
        }
    },
    "inputs": {
        "train": "s3://<s3-bucket>/train.csv/",  # replace
        "test": "s3://<s3-bucket>/test.csv/",  # replace
    }
}

config['ecs_task_definition'] = {
    "requiresCompatibilities": [
        "FARGATE"
    ],
    "memory": "8192",
    "cpu": "4096",
    "containerDefinitions": [{
        "name": "EC2TFInference",
        "image": "690669119032.dkr.ecr.cn-north-1.amazonaws.com.cn/gw-infer:20201129041237",
        "environment": [
            {
                "name": "MODEL_S3_KEY",
                "value": "s3://leigh-gw/dkn_model/dkn-2020-11-28-06-41-17-782/output/model.tar.gz"
            }
        ],
        "essential": True,
        "portMappings": [{
            "hostPort": 8500,
            "protocol": "tcp",
            "containerPort": 8500
        },
            {
                "hostPort": 8501,
                "protocol": "tcp",
                "containerPort": 8501
            },
            {
                "containerPort": 80,
                "protocol": "tcp"
            }
        ],
        "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
                "awslogs-group": "gw-logs",
                "awslogs-region": "<region-name>",
                "awslogs-stream-prefix": "inference"
            }
        }
    }],
    "volumes": [],
    "networkMode": "awsvpc",
    "placementConstraints": [],
    "family": "GW-DKN-infer",
    "executionRoleArn": "arn:aws:iam::662566784674:role/ecsTaskExecutionRole"
}

config['run_task'] = {
    'cluster': 'arn:aws:ecs:<region-name>:662566784674:cluster/GW',
    'taskDefinition': 'arn:aws:ecs:<region-name>:662566784674:task-definition/GW-DKN-infer:1',
    'count': 1,
    'launchType': 'FARGATE',
    'networkConfiguration': {
        'awsvpcConfiguration': {
            'subnets': [
                'subnet-2223d109',  # replace
            ],
            'securityGroups': [
                'sg-3096484f',  # replace
            ],
            'assignPublicIp': 'ENABLED'
        }
    },
    'overrides': {
        'executionRoleArn': 'arn:aws:iam::662566784674:role/ecsTaskExecutionRole',  # replace with S3 get permission
        'taskRoleArn': 'arn:aws:iam::662566784674:role/ecsTaskExecutionRole',  # replace
    }
}

config['ecs_service_update'] = {
    "cluster": "GW",
    "forceNewDeployment": True,
    "service": "gw",
    "taskDefinition": ""
}
