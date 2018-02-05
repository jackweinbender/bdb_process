default:

build: clean
	@ python3 process_page.py bdb_pages/01_hebrew

test: clean
	@ python3 process_page.py test_pages

get-images:
	@ wget https://storage.googleapis.com/dictionary-nearline/bdb_raw.zip
	@ unzip bdb_raw.zip
	@ rm -rf bdb_raw.zip

clean:
	@ rm -rf _*
