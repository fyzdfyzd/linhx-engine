# Anh Frappe v15 + app linhx_worker. Dung tren VM (khong can GitHub, chi Docker Hub + PyPI).
ARG FRAPPE_IMAGE=frappe/erpnext:v15
FROM ${FRAPPE_IMAGE}
USER frappe
WORKDIR /home/frappe/frappe-bench
COPY --chown=frappe:frappe apps/linhx_worker apps/linhx_worker
RUN env/bin/pip install --quiet --no-build-isolation --no-deps -e apps/linhx_worker \
 && (grep -qx linhx_worker sites/apps.txt || echo linhx_worker >> sites/apps.txt)
