# Thin wrapper over ./run.sh so `make <target>` works where make is installed.
# The CANONICAL entrypoint is ./run.sh — the host needs only Docker; make is optional.
.DEFAULT_GOAL := help
.PHONY: help build shell demo-1 demo-2 demo-3 viz rqt slides slides-research slides-pdf test clean

help build shell demo-1 demo-2 demo-3 viz rqt slides slides-research slides-pdf test clean:
	@./run.sh $@
