# GW-RecSys
## 镜像列表
| 编号 | 名字 | 内容 | 文件夹 | 完成度 |
| ---- | ---- | ---- | ---- | ---- |
| 1 | KG 训练 | 知识图谱训练，生成context/entity/word embeddings.npy| graph/train | [x] |
| 2 | KG 推理 | 知识图谱推理，将单条新闻标题转化为word/entity的索引| graph/inference | [x] |
| 3 | KG 逻辑 | 知识图谱推理调用，将新闻标题转化为word/entity的索引| graph/logic | [] |

## 使用方法
#### KG 训练
##### 通过boto3的方法进行调用，详情参考 graph/train/test_train.ipynb
#### KG 推理
##### 通过boto3的方法进行调用，详情参考 graph/inference/test_inference.ipynb