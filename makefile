default:

test: clean
	@ ./process_page.py test_pages

clean:
	@ rm -rf test_pages/_*