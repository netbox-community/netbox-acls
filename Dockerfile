ARG NETBOX_VARIANT=v4.5

FROM netboxcommunity/netbox:${NETBOX_VARIANT}

RUN mkdir -pv /plugins/netbox-acls
COPY . /plugins/netbox-acls

RUN /usr/local/bin/uv pip install --editable /plugins/netbox-acls
