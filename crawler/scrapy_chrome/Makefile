gen_urls:
	python scrapy_chrome/config/extension_list.py generate

load_urls:
	python scrapy_chrome/config/extension_list.py load

crawl:
	# Generate extension URLs if config/var directory doesn't exist or is empty
	if [ ! -d "scrapy_chrome/config/var" ] || [ -z "$(ls -A scrapy_chrome/config/var/*.json 2>/dev/null)" ]; then \
		$(MAKE) gen_urls; \
	fi;

	scrapy crawl extension_detail -L WARNING

test:
	pytest -s

shell:
	https_proxy=http://127.0.0.1:7890 scrapy shell "https://chromewebstore.google.com/detail/meeting-assistant-chatgpt/kdkohcmkkplmkknlelglhfhjkegkiljd"