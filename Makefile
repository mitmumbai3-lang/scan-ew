.PHONY: install test benchmark run clean

install:
	pip install -r requirements.txt
	cd web && npm install

test:
	python -m pytest tests/ -v

benchmark:
	python scripts/run_benchmarks.py

run:
	python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 & \
	cd web && npm run dev -- --host 0.0.0.0 --port 5173

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache web/dist
