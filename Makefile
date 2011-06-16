blog = proxychains ./blog.py
all: blog.post
list: 
	$(blog) list
%.post: %.org
	$(blog) post $<
