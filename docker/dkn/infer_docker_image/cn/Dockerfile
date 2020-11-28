FROM python:3.7.9-slim
RUN pip install boto3

FROM tensorflow/serving
COPY --from=0 / /

ADD ./copy_model.py /usr/bin
ENTRYPOINT ["sh", "-c"]