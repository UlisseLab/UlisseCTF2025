chall:
	@echo "Creating virtual environment..."
	python3 -m venv wordfreq
	@echo "Activating virtual environment..."
	@source wordfreq/bin/activate && pip install pycryptodome wordfreq
	@echo "Running the challenge script..."
	@source wordfreq/bin/activate && FLAG="UlisseCTF{spinm3rightround'b4by'rightround}" python challenge.py > ../attachments/output.txt
	@echo "Output saved to ../attachments/output.txt"
	@cp challenge.py ../attachments/challenge.py
	@echo "copied script to ../attachments/challenge.py"
	@echo "Deactivating virtual environment..."
	@echo "Cleaning up virtual environment..."
	@rm -rf wordfreq

clean:
	@echo "Removing output file..."
	@rm -f  ../attachments/*
	@rm -rf wordfreq
	@echo "Clean up complete."
