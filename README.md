.

    Ranking Method based on Knowledge-graph

    ├── README.md
    
    ├── airflow: task orchestration based on airflow
        └── airflow_sample
        ├── airflow_dag.py
        ├── build_and_push.sh
        └── container

    ├── cdk: cdk code for the infra of recommender system based on ECS
        └── aoyu_cdk_sample
            ├── README.md
            ├── app.py
            ├── armvp
            ├── cdk.json
            ├── lambda
            ├── requirements.txt
            ├── setup.py
            ├── source.bat
            └── tests

    └── docker: core images for ranking algorithm based on knowledge graph
        ├── dkn
            ├── Dockerfile
            ├── build_and_push.sh
            ├── recsys_kg_byoc.ipynb
            ├── recsys_kg_demo.ipynb
            └── recsys_tools
        └── graph
            ├── byoc
            ├── encoding.py
            ├── kg
            ├── kg.py
            ├── requirements.txt
            ├── test_image.ipynb
            └── vocab.json

14 directories, 18 files
