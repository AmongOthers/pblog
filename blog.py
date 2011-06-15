#!/usr/bin/python2
'''
Usages:
./blog.py list
./blog.py post post.html
'''
import sys
import xmlrpclib
import re
import mimetypes
import os.path

serviceUrl, appKey = 'http://www.cnblogs.com/ans42/services/metaweblog.aspx', 'ans42'
usr, passwd = 'ans42', 'iambook11'
# serviceUrl, appKey = 'http://blog.csdn.net/huafengxi/services/MetaBlogApi.aspx', 'huafengxi'
# usr, passwd = 'huafengxi', 'iambook11'

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
        return self.server.metaWeblog.editPost(id, self.usr, self.passwd, dict(kw, title=title, description=description, category=category), publish)

    def newMediaObject(self, path, name=None, blogid=''):
        with open(os.path.expanduser(path)) as f:
            content = xmlrpclib.Binary(f.read())
        type,_ = mimetypes.guess_type(path)
        name = name or os.path.basename(path)
        return self.server.metaWeblog.newMediaObject(blogid, self.usr, self.passwd, dict(name=name, type=type, bits=content))

    def post(self, path):
        with open(os.path.expanduser(path)) as f:
            content = f.read()
        m = re.search('<(?:title|TITLE)>(.*?)</(?:title|TITLE)>', content)
        title = m and m.group(1) and 'Default Title'
        return self.newPost(title, content)

    def list(self):
        for p in blog.getRecentPosts(10):
            print '%(postid)s\t', p
        
    def __repr__(self):
        return 'MetaWeblog(%s, %s, %s)'%(repr(self.serviceUrl), repr(self.usr), repr(self.passwd))
    
if __name__ == '__main__':
    blog = MetaWeblog(serviceUrl, appKey, usr, passwd)
    if len(sys.argv) < 2 or not hasattr(blog, sys.argv[1]): sys.stderr.write(__doc__)
    else: getattr(blog, sys.argv[1])(*sys.argv[2:])
    # print blog.newPost(publish=False) 
    # print blog.newPost() 
    # print blog.newMediaObject('~/res/bg.jpg')
    #print blog.getUsersBlogs()
    # blog.post('test.html')
    # for p in blog.getRecentPosts(100):
    #     print p
        #blog.deletePost(p['postid'])
        # print blog.editPost(p['postid'], title='Title edited for testing')
