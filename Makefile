NAME=SciPass
VERSION=1.0.0

rpm:	dist
	rpmbuild -ta dist/$(NAME)-$(VERSION).tar.gz
	rm -rf dist

clean:
	rm -rf dist/$(NAME)-$(VERSION)
	rm -rf dist

test:
	cd python; python -m coverage run --source=./ --omit=__init__.py,*Test.py,t/SciPass.py t/SciPassTest.py; python -m coverage report -m; python -m coverage xml;python -m coverage annotate; python -m coverage html;

test_mininet:
	cd python; python -m coverage run --source=./ --omit=__init__.py,*Test.py,t/SciPass.py t/SciPassTest_mininet.py; coverage report -m; python -m coverage xml;python -m coverage annotate; python -m coverage html;

dist:
	rm -rf dist/$(NAME)-$(VERSION)
	mkdir -p dist/$(NAME)-$(VERSION)
	cp -r etc/ python/ SciPass.spec dist/$(NAME)-$(VERSION)/
	cd dist; tar -czvf $(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)/ --exclude .svn
