#!/usr/bin/env python
# encoding: utf-8
from localuser import UserImgCache
import logging
logging.basicConfig(level=logging.INFO)
import hashlib
# UserImgCache

class Test_UserImgCache:
    def setup_method(self,method):
        self.user_img = UserImgCache()
    def test_set_user_img(self):
        group_user_id = "100"
        img_data = buffer("test")
        url = self.user_img.set_user_img(group_user_id,img_data)
        logging.info(("create , url:",url)) # 下载下来确实是test

    def test_get_user_img_with_user_id(self):
        group_user_id = "100"
        url = self.user_img.get_user_img_with_user_id(group_user_id)
        logging.info(("with user id , url:",url))

    def test_get_user_img_with_img_md5(self):
        img_data = buffer("test")
        img_md5= hashlib.md5(img_data).hexdigest()
        url = self.user_img.get_user_img_with_img_md5(img_md5)
        logging.info(("with img md5 , url:",url)) # None

def main():
    pass
if __name__ == '__main__':
    main()
