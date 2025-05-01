tshark -r capture_censored.pcap -Y json -T fields -e http.file_data | xxd -r -p | jq
