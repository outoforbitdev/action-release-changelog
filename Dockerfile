FROM python:3.12.9-bookworm

RUN python -m pip install PyGithub
COPY src /src
RUN chmod -R +x /src
RUN sh /src/tests.sh

ENTRYPOINT ["src/entrypoint.sh"]
