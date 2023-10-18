# Makefile for Journal Migration

.PHONY: stg-migration prd-migration dev-migration help all clean test

help:
	@echo "Usage:"
	@echo "  make stg-migration journal=<journal_id>  - Run stg migration for a specific journal"
	@echo "  make prd-migration journal=<journal_id>  - Run prd migration for a specific journal"
	@echo "  make dev-migration journal=<journal_id>  - Run dev migration for a specific journal"
	@echo "eg: make stg-migration journal=ucb_crp_bpj"

migration-command = python -m journal_transporter transfer --source ojs-$(1) --target janeway-$(1) --journals $2 --log e --on-error c --force >> $2_$(1)_output.log

start-message = echo "----> Start Time: $$(date)" >> $2_$(1)_output.log
end-message = echo "----> End Time: $$(date)" >> $2_$(1)_output.log

# init-migration: ensure necessary setup and check server reachability
#  Param 1: environment (dev/stg/prd)
#  Param 2: command to execute
define init-migration
        # start a Pipenv shell if it is not already started
	@if [ -z "$$(pipenv --venv)" ]; then \
		echo "Starting Pipenv shell..."; \
		pipenv shell; \
	fi
	# if the environment is prd, provide a helpful hint
	@if [ "$(1)" = "prd" ]; then \
		echo "🚀 If prompted for a password, it can be found on submit-prd:apache/htdocs/ojs/config.inc.php"; \
		echo "NOTE: it's safe to abort with ctrl-c at this point, and rerun make prd-migration when you have the password."
	fi
	# check if the server is reachable
	curl -Is https://pub-submit2-$(1).escholarship.org/ojs/index.php/pages/jt/api/journals | head -n 1 | grep "200 OK" > /dev/null || (echo "Server not reachable." && exit 1)
	# now run whatever command was passed to this function, typically start-message
	$2
endef

dev-migration:
	$(call init-migration, dev, $(start-message) && $(migration-command, dev, $(journal)) && $(end-message))

stg-migration:
	$(call init-migration, stg, $(start-message) && $(migration-command, stg, $(journal)) && $(end-message))

prd-migration:
	$(call init-migration, prd, $(start-message) && $(migration-command, prd, $(journal)) && $(end-message))

