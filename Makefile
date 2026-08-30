.PHONY: build qa preview preflight deploy-staging deploy-production
build:
	python3 build.py
qa:
	python3 scripts/qa_static.py
preview: build qa
	python3 -m http.server 8080 -d dist
preflight:
	python3 scripts/preflight.py

deploy-staging:
	./scripts/deploy-pi5.sh staging

deploy-production:
	./scripts/deploy-pi5.sh production
