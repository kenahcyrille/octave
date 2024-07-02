# Makefile for Octave project

# Define the Octave binary path. Update this if necessary.
OCTAVE_BIN = $(PKG_INSTALL_DIR)/bin/octave

# List of Octave script files
SCRIPTS = script1.m script2.m

# Target to run all Octave scripts
run: $(SCRIPTS)
	$(OCTAVE_BIN) --eval "for script in {'$(SCRIPTS)'}; disp(['Running ', script{1}]); run(script{1}); end"

# Target to run a specific Octave script
run_script1: script1.m
	$(OCTAVE_BIN) --eval "run('script1.m')"

run_script2: script2.m
	$(OCTAVE_BIN) --eval "run('script2.m')"

# Target to clean up generated files (if any)
clean:
	rm -f *.oct *.o

# Phony targets to prevent conflicts with file names
.PHONY: run run_script1 run_script2 clean
