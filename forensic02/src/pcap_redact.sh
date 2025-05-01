#!/bin/sh

cat capture.pcap \
	| sed 's%/app/[a-zA-Z0-9]\{7\}-[a-zA-Z0-9]\{32\}/subscribe%/app/REDACTE-DREDACTEDREDACTEDREDACTEDREDACTE/subscribe%g' \
	| sed 's%/appliance/[a-zA-Z0-9]\{32\}/publish%/appliance/REDACTEDREDACTEDREDACTEDREDACTED/publish%g' \
	| sed 's%"sign":"[a-zA-Z0-9]\{32\}"%"sign":"REDACTEDREDACTEDREDACTEDREDACTED"%g' \
	| sed 's%"messageId":"[a-zA-Z0-9]\{32\}"%"messageId":"REDACTEDREDACTEDREDACTEDREDACTED"%g' \
	> capture_censored.pcap
