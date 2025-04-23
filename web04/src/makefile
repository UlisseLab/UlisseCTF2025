include web/.env
all: flag distribute

flag:
	echo $(FLAG) > ./../flags.txt

clean:
	rm -rdf attachments/*

distribute: clean
	sh scripts/distribute.sh ".."
