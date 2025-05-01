#!/bin/sh
socat TCP-LISTEN:4456,reuseaddr,fork EXEC:"python server.py"
