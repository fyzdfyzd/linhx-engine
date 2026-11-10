# Anh Frappe v15 + cac app linhx_* + cli linhx_cli. Dung tren VM (khong can GitHub, chi Docker Hub + PyPI).
ARG FRAPPE_IMAGE=frappe/erpnext:v15
FROM ${FRAPPE_IMAGE}
USER frappe
WORKDIR /home/frappe/frappe-bench
COPY --chown=frappe:frappe apps apps
COPY --chown=frappe:frappe cli cli
COPY --chown=frappe:frappe deploy/sites deploy/sites
RUN env/bin/pip install --quiet --no-build-isolation --no-deps -e cli $(for d in apps/linhx_*; do [ -f "$d/pyproject.toml" ] && printf ' -e %s' "$d"; done) \
 && for d in apps/linhx_*; do [ -d "$d" ] && a=$(basename "$d") && (grep -qx "$a" sites/apps.txt || echo "$a" >> sites/apps.txt); done
