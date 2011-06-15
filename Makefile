blog = proxychains ./blog.py
all: test
test: 
	$(blog) list
%.post: %.html
	$(blog) post $<
%.html: %.org
	emacs   --batch --execute "(require 'org) (setq org-export-headline-levels 2)" --visit=test.org --funcall org-export-as-html-batch