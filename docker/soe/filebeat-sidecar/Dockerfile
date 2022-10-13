
# version tag should match our ELK stack, for major version at least
# https://www.docker.elastic.co/
FROM docker.elastic.co/beats/filebeat:6.4.3

COPY --chown=root:filebeat filebeat.yml /usr/share/filebeat/filebeat.yml

# nginx logs are not world-readable - adding filebat to 'adm' group allows reading
# nginx logs on a shared volume
USER root
RUN usermod -a -G adm filebeat

USER filebeat

