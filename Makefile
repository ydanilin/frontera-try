crawl:
	scrapy crawl wlw
init:
	rm -f wlwjob.db  # -f flag checks if file exists
	python -m frontera.utils.add_seeds --config tutorial.frontera.settings --seeds-file seeds.txt
once:
	scrapy crawl wlw -s CLOSESPIDER_PAGECOUNT=1
test:
	python -m unittest discover -s ./tutorial/tests
