# Anh Frappe v15 + app linhx_core, linhx_worker + cli linhx_cli. Dung tren VM (khong can GitHub, chi Docker Hub + PyPI).
ARG FRAPPE_IMAGE=frappe/erpnext:v15
FROM ${FRAPPE_IMAGE}
USER frappe
WORKDIR /home/frappe/frappe-bench
COPY --chown=frappe:frappe apps/linhx_core apps/linhx_core
COPY --chown=frappe:frappe apps/linhx_worker apps/linhx_worker
COPY --chown=frappe:frappe cli cli
COPY --chown=frappe:frappe deploy/sites deploy/sites
RUN env/bin/pip install --quiet --no-build-isolation --no-deps -e apps/linhx_core -e apps/linhx_worker -e cli \
 && (grep -qx linhx_core sites/apps.txt || echo linhx_core >> sites/apps.txt) \
 && (grep -qx linhx_worker sites/apps.txt || echo linhx_worker >> sites/apps.txt)
