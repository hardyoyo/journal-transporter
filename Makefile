# Makefile for Journal Migration

.PHONY: stg-migration prd-migration dev-migration help watch status all clean test

help:
	@echo "Usage:"
	@echo "  make stg-migration journal=<journal_id>  - Run stg migration for a specific journal"
	@echo "  make prd-migration journal=<journal_id>  - Run prd migration for a specific journal"
	@echo "  make dev-migration journal=<journal_id>  - Run dev migration for a specific journal"
	@echo "  make watch  - Watch the log file for the currently running migration"
	@echo "  make status  - Check the status of the currently running migration"
	@echo ""
	@echo "  Example:"
	@echo "    make stg-migration journal=ucb_crp_bpj"
	@echo "    make watch"
	@echo ""

define find_running_migration
	$$(ps aux | grep "python -m journal_transporter transfer" | grep -v grep)
endef

define extract_journal_from_migration
	$$(echo $$1 | sed -nE 's/.*journal=([^ ]+).*/\1/p')
endef

define find_log_file
	$$(find . -name "$$1*_output.log" 2>/dev/null | head -n 1)
endef

dev-migration:
	$(call init-migration, dev, $(start-message) && $(migration-command, dev, $(journal)) && $(end-message))

stg-migration:
	$(call init-migration, stg, $(start-message) && $(migration-command, stg, $(journal)) && $(end-message))

prd-migration:
	$(call init-migration, prd, $(start-message) && $(migration-command, prd, $(journal)) && $(end-message))

watch:
	@running_migration=$$($(call find_running_migration)); \
	if [ -n "$$running_migration" ]; then \
		journal=$$($(call extract_journal_from_migration,$$running_migration)); \
		log_file=$$($(call find_log_file,$$journal)); \
		if [ -n "$$log_file" ]; then \
			echo "Watching the log file $$log_file for the currently running migration..."; \
			tail -f $$log_file; \
		else \
			echo "Migration log file not found."; \
		fi; \
	else \
		echo "No active migration found."; \
	fi

status:
	@running_migration=$$($(call find_running_migration)); \
	if [ -n "$$running_migration" ]; then \
		journal=$$($(call extract_journal_from_migration,$$running_migration)); \
		log_file=$$($(call find_log_file,$$journal)); \
		if [ -n "$$log_file" ]; then \
			echo "Active migration found for journal: $$journal"; \
			echo "Checking status for $$journal..."; \
			echo "Migration is currently running."; \
			echo "----> Started: $$(grep "Start Time" $$log_file | sed 's/^----> Start Time: //')"; \
			echo "----> Elapsed Time: $$(date -u -d @$$(($(date -u +"%s") - $$(date -u -d @$$(grep "Start Time" $$log_file | sed 's/^----> Start Time: //')" +"%s")))) -u +%H:%M:%S"; \
		else \
			echo "Migration log file not found."; \
		fi; \
	else \
		echo "No active migration found."; \
	fi

