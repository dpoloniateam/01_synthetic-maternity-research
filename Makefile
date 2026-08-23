
# --- Synthetic Design Laboratory 2 (23 Aug 2026) ---
sdl2-check:      ## offline checks: administration of V4_R1, canonical dimensions, config
	python run_experiment.py --arm P --check
sdl2-test:       ## unit tests of the developments
	python -m pytest tests/test_developments.py -q
sdl2-pilot:      ## 30 sessions, 3 repetitions, arm P (costs money; halts at USD 50)
	python run_experiment.py --arm P --limit 30 --repetitions 3 --stage all
sdl2-image:      ## build the container image
	docker build -t sdl2:latest .
