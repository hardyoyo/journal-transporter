# Makefile for Journal Migration

.SILENT:
.PHONY: stg-migration prd-migration dev-migration help test all clean

help:
	@echo "Usage:"
	@echo "  make stg-migration journal=<journal_id>  - Run stg migration for a specific journal"
	@echo "  make prd-migration journal=<journal_id>  - Run prd migration for a specific journal"
	@echo "  make dev-migration journal=<journal_id>  - Run dev migration for a specific journal"
	@echo ""
	@echo "  Example:"
	@echo "    make dev-migration journal=ucb_crp_bpj"
	@echo ""
	@echo "  HINT: You can do a 'dry run' by using the -n flag for make."
	@echo ""

migration-command = python -m journal_transporter transfer --source ojs-$(strip $(1)) --target janeway-$(strip $(3)) --journals $2 --log e --on-error c --force >> $2_$(strip $(1))_output.log

start-message = echo "----> Start Time: $$(date)" >> $2_$(strip $(1))_output.log
end-message = echo "----> End Time: $$(date)" >> $2_$(strip $(1))_output.log

# run-migration: ensure necessary setup and check server reachability, then run the migration
#  Param 1: source environment (dev/stg/prd)
#  Param 2: journal ID
#  Param 3: target environment
define run-migration
        # Check if Pipenv is not activated
        if [ -z "$$VIRTUAL_ENV" ]; then \
            echo "Starting Pipenv shell..."; \
            echo "NOTE: you'll have to re-run this make command, after the Pipenv shell is started."; \
            pipenv shell; \
        fi
        # if the source environment is prd, provide a helpful hint
        @if [ "$(strip $(1))" = "prd" ]; then \
            echo "🚀 If prompted for a password, it can be found on submit-prd:apache/htdocs/ojs/config.inc.php"; \
            echo "NOTE: it's safe to abort with ctrl-c at this point, and rerun make prd-migration when you have the password."; \
            curl -u apiuser -Is https://pub-submit2-prd.escholarship.org/ojs/index.php/pages/jt/api/journals  | grep "200 OK" > /dev/null || (echo "Server not reachable." && exit 1); \
        else \
            curl -Is https://pub-submit2-$(strip $(1)).escholarship.org/ojs/index.php/pages/jt/api/journals | head -n 1 | grep "200 OK" > /dev/null || (echo "Server not reachable." && exit 1); \
        fi
        # now run the migration command
        $(start-message) && $(migration-command) && $(end-message)
endef

dev-migration:
	$(call run-migration, dev, $(journal), dev) &

stg-migration:
	$(call run-migration, stg, $(journal), stg) &

prd-migration:
	$(call run-migration, prd, $(journal), prd) &

