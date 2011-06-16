#!/usr/bin/python2
'''
Usages:
./blog.py list
./blog.py post post.[org|adoc|html]
'''
import sys
import xmlrpclib
import re
import mimetypes
import os.path
import hashlib
from subprocess import Popen, PIPE, STDOUT

serviceUrl, appKey = 'http://www.cnblogs.com/ans42/services/metaweblog.aspx', 'ans42'
usr, passwd = 'ans42', 'iambook11'
# serviceUrl, appKey = 'http://blog.csdn.net/huafengxi/services/MetaBlogApi.aspx', 'huafengxi'
# usr, passwd = 'huafengxi', 'iambook11'

def read(path):
    try:
        with open(path) as f:
            return f.read()
    except IOError:
            return ''
    
def popen(cmd):
    print cmd
    return Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT).communicate()[0]

def chext(path, ext):
    return re.sub(r'(\.[^/.]*)$', ext, path)

def get_ext(name):
    index = name.rfind('.')
    if index == -1: return ""
    return name[index+1:].lower()

def mv(src, target):
    return popen('mv %s %s'%(src, target))
    
def md5(str):
    return hashlib.md5(str).hexdigest()

def is_updated(path, md5):
    return md5(read(path)) != read(md5)

def mkfile(src, target, handler):
    dep = target + '.dep'
    if not is_updated(src, dep): return False
    handler(src, target)
    write(dep, md5(src))
    return True

def org2html(src, target):
    output = popen('''emacs --batch --execute '(require `org)' --visit=%s --execute '(progn (setq org-export-headline-levels 2) (setq org-export-html-postamble "") (setq org-export-html-preamble "") (setq org-export-htmlize-output-type `css) (setq org-export-html-style "<link rel=\\"stylesheet\\" type=\\"text/css\\" href=\\"org.css\\">") (org-export-as-html-batch))' '''%(src))
    mv(chext(src, '.html'), target)
    return output

def html2html(src, target):
    return mv(src, target)

def adoc2html(src, target):
    return popen('asciidoc %s -o %s'%(src, target))
    
def to_html(path, target):
    handlers = dict(htm=html2html, html=html2html, adoc=adoc2html, asciidoc=adoc2html, org=org2html)
    f = handlers.get(get_ext(path))
    if not f: raise Exception('do not know how to make html from %s'%path)
    return f(path, target)

class MetaWeblog:
    '''works with www.cnblogs.com atleast'''
    def __init__(self, serviceUrl, appKey, usr, passwd):
        self.serviceUrl, self.appKey, self.usr, self.passwd = serviceUrl, appKey, usr, passwd
        self.server = xmlrpclib.ServerProxy(self.serviceUrl)

    def getUsersBlogs(self):
        return self.server.blogger.getUsersBlogs(self.appKey, self.usr, self.passwd)
    
    def getCategories(self, blogid=''):
         return self.server.metaWeblog.getCategories(blogid, self.usr, self.passwd)

    def getRecentPosts(self, count=5, blogid=''):
        return self.server.metaWeblog.getRecentPosts(blogid, self.usr, self.passwd, count)
        
    def deletePost(self, id):
        return self.server.blogger.deletePost(self.appKey, id, self.usr, self.passwd, False)
    
    def getPost(self, id):
        return self.server.metaWeblog.getPost(id, self.usr, self.passwd)
        
    def newPost(self, title='Title used for test', description='this is a test post.', category='no category', publish=True, blogid='', **kw):
        return self.server.metaWeblog.newPost(blogid, self.usr, self.passwd, dict(kw, title=title, description=description, category=category), publish)

    def editPost(self, id, title='Title used for test', description='this is a test post.', category='no category', publish=True, **kw):
        print id, title, kw, self.usr, self.passwd, publish, category
        return self.server.metaWeblog.editPost(id, self.usr, self.passwd, dict(kw, title=title, description=description, category=category), publish)

    def newMediaObject(self, path, name=None, blogid=''):
        with open(os.path.expanduser(path)) as f:
            content = xmlrpclib.Binary(f.read())
        type,_ = mimetypes.guess_type(path)
        name = name or os.path.basename(path)
        return self.server.metaWeblog.newMediaObject(blogid, self.usr, self.passwd, dict(name=name, type=type, bits=content))

    def post(self, path):
        html = chext(path, '.html')
        print to_html(path, html)
        content = read(html)
        m = re.search('<(?:title|TITLE)>(.*?)</(?:title|TITLE)>', content)
        title = m and m.group(1) or 'Default Title'
        description = content
        # matched = filter(lambda p: p['title'] == title,  self.getRecentPosts(10))
        # if matched:
        #     return self.editPost(matched[0]['postid'], title, description)
        # else:
        #     return self.newPost(title, description)

    def list(self, count=10):
        for p in self.getRecentPosts(count):
            print '%(postid)s\t%(title)s\n%(description)s'%p
        
    def __repr__(self):
        return 'MetaWeblog(%s, %s, %s)'%(repr(self.serviceUrl), repr(self.usr), repr(self.passwd))
    
if __name__ == '__main__':
    blog = MetaWeblog(serviceUrl, appKey, usr, passwd)
    if len(sys.argv) < 2 or not hasattr(blog, sys.argv[1]): sys.stderr.write(__doc__)
    else: getattr(blog, sys.argv[1])(*sys.argv[2:])
