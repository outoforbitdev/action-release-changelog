FROM python:3.13.3-bookworm

RUN python -m pip install PyGithub
COPY src /src
RUN chmod -R +x /src
RUN sh /src/tests.sh

ENTRYPOINT ["/src/entrypoint.sh"]
