default:

build: clean
	@ ./process_page.py images_raw_ppm/01_dictionary

test: clean
	@ ./process_page.py test_pages

clean:
	@ rm -rf test_pages/_*