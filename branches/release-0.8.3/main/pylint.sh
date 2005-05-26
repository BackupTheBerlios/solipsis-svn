#!/bin/sh

pylint \
	--method-rgx=".*" \
	--min-name-length=1 \
	solipsis
