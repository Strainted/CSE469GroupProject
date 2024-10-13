CC = python3
SRC = main.py
BIN = bchoc

all: $(BIN)

$(BIN): $(SRC)
	@echo "Creating executable..."
	@echo "#!/usr/bin/env python3" > $(BIN)
	@cat $(SRC) >> $(BIN)
	@chmod +x $(BIN)

clean:
	@echo "Cleaning up..."
	rm -f $(BIN)
