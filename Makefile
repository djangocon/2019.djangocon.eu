.ONESHELL:
django-base-template: hugo
	cp hugo_site/public/django-base-template/index.html dceu2019/src/dceu2019/templates/base.html
	sed -i 's/¤{/{/g' dceu2019/src/dceu2019/templates/base.html
	sed -i 's/¤}/}/g' dceu2019/src/dceu2019/templates/base.html
	cp -r hugo_site/public/static/* dceu2019/src/dceu2019/static/

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
