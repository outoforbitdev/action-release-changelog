FROM python:3.12.9-bookworm

RUN python -m pip install requests
COPY create_release.py /create_release.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN chmod +x /create_release.py

ENTRYPOINT ["/entrypoint.sh"]