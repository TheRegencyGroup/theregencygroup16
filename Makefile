IMAGE_ODOO:=quay.io/opsway/odoo:regency

all: build push

build:
	docker build --pull -t ${IMAGE_ODOO} .

push:
	docker push ${IMAGE_ODOO}
