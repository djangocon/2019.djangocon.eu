.ONESHELL:
django-base-template: hugo
	cp hugo_site/public/django-base-template/index.html dceu2019/src/dceu2019/templates/base.html

.ONESHELL:
hugo:
	cd hugo_site
	hugo
	cd ..

.ONESHELL:
hugo-serve:
	cd hugo_site
	hugo server
	cd ..
