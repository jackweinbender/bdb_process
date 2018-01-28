default:

build: clean
	@ python3 process_page.py images_raw_ppm/01_dictionary

test: clean
	@ python3 process_page.py test_pages

get-images:
	@ wget https://storage.googleapis.com/dictionary-nearline/images_raw_ppm.zip
	@ unzip images_raw_ppm.zip
	@ rm -rf images_raw_ppm.zip

clean:
	@ rm -rf _*
