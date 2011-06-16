blog = proxychains ./blog.py
all: Readme.post
list: 
	$(blog) list
%.post: %.org
	$(blog) post $<
