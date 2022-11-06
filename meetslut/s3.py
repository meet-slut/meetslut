# -*- coding: utf-8 -*-
# @Author: Chen Renjie
# @Date:   2022-07-22 19:47:54
# @Last Modified by:   Chen Renjie
# @Last Modified time: 2022-07-31 11:37:54

import os
import boto3
import requests
# pip install python-magic-bin==0.4.14



class S3(object):
    def __init__(self, ak, sk, endpoint_url):
        self.ak = ak
        self.sk = sk
        self.endpoint_url = endpoint_url

        self.client = boto3.client(
            's3',
            aws_access_key_id = ak,
            aws_secret_access_key = sk,
            endpoint_url = endpoint_url,
            region_name='cn',
        )

    # 确认存储桶
    def head_bucket(self, bucket):
        try:
            r = self.client.head_bucket(Bucket=bucket)
            # print(r['RetryAttempts'])
            return r is not None
        except Exception as e:
            print(e)
            return False

    # 列举存储桶 '%Y-%m-%d %H:%M:%S'
    def list_buckets(self, fmt=None):
        r = self.client.list_buckets()
        owner = f"{r['Owner']['DisplayName']}({r['Owner']['ID']})"
        if isinstance(fmt, str):
            t = lambda x: x.strftime(fmt)
        else:
            t = lambda x: x

        buckets = [(b['Name'], t(b['CreationDate'])) for b in r['Buckets']]
        return buckets, owner

    # 创建存储桶
    def create_bucket(self, bucket):
        assert not self.head_bucket, "Bucket already exists"
        raise NotImplementedError

    # 删除存储桶
    def delete_bucket(self, bucket):
        assert self.head_bucket, "Bucket not exists"
        raise NotImplementedError

    def get_bucket_acl(self, bucket):
        r = self.client.get_bucket_acl(
            Bucket=bucket
        )
        permission = r['Grants'][0]['Permission']
        return permission

    def list_objects(self, bucket):
        raise NotImplementedError

    def head_object(self, bucket, key):
        try:
            r = self.client.head_object(Bucket=bucket, Key=key)
            # print(r['RetryAttempts'])
            return r is not None
        except Exception as e:
            print(e)
            return False

    def get_object(self, bucket, key):
        r = self.client.get_object(Bucket=bucket, Key=key)
        body = r['Body'].read()
        return body

    def put_object(self, bucket, key, body):
        assert not self.head_object(bucket, key)
        r = self.client.put_object(
            Bucket=bucket, Key=key, Body=body
            # ContentType
        )
        print(r)
        return True

    def delete_object(self, bucket, key):
        assert self.head_object(bucket, key)
        r = self.client.delete_object(Bucket=bucket, Key=key)
        return r is not None

    def download(self, bucket, key, f):
        assert isinstance(f, (str, bytes))
        if isinstance(f, str):
            self.client.download_file(Bucket=bucket, Key=key, Filename=f)
        elif isinstance(f, bytes):
            self.client.download_fileobj(Bucket=bucket, Key=key, Fileobj=f)
        else:
            pass
        # with open(filename, 'wb') as data:
        #     self.client.download_fileobj(Bucket=bucket, Key=key, Fileobj=data)

    def upload(self, f, bucket, key):
        assert isinstance(f, (str, bytes))
        if isinstance(f, str):
            self.client.upload_file(Filename=f, Bucket=bucket, Key=key)
        elif isinstance(f, bytes):
            self.client.upload_fileobj(Fileobj=f, Bucket=bucket, Key=key)
        else:
            pass

    def transfer(self, url, bucket, filename=None, folder=None):
        filename = filename or os.path.basename(url)
        key = filename if folder is None else os.path.join(folder, filename)
        assert not self.head_object(bucket, key), f"file {key} exists!"
        r = requests.get(url, headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        })
        body = r.content
        content_type = r.headers["Content-Type"]
        r = self.client.put_object(
            Bucket=bucket, Key=key, Body=body,
            ContentType=content_type
        )
        print(r['ETag'], r['VersionId'])


"""土星云

https://saturncloud.com.cn/
"""

class Saturn(S3):
    def __init__(self, ak, sk, endpoint_url="https://s3.cn-global-0.xxyy.co:16000"):
        super(Saturn, self).__init__(ak, sk, endpoint_url)

    def list_objects(self, name):
        # assert self.head_bucket(name), "Bucket not exists"
        r = self.client.list_objects_v2(
            Bucket=name,
            # Delimiter='/',
            # MaxKeys=2,
        )
        print(r)

    def create_bucket(self, name):
        pass

    def head_object(self, bucket, key):
        r = self.client.head_object(Bucket=bucket, Key=key)
        print(r)




class Qiniu(S3):
    def __init__(self, ak, sk, endpoint_url="https://s3.cn-global-0.xxyy.co:16000"):
        super(Qiniu, self).__init__(ak, sk, endpoint_url)

    def list_objects(self, bucket):
        assert self.head_bucket(bucket), "Bucket not exists"
        r = self.client.list_objects_v2(
            Bucket=bucket,
            # Delimiter='/',
            # MaxKeys=2,
        )
        contents = [(c['Key'], c['Size']) for c in r["Contents"]]
        assert len(contents) == r["KeyCount"]
        return contents

    def create_bucket(self, bucket):
        pass

class BackBlaze(S3):
    def __init__(self, ak, sk, endpoint_url="https://s3.cn-global-0.xxyy.co:16000"):
        super(BackBlaze, self).__init__(ak, sk, endpoint_url)



if __name__ == '__main__':

    # AK = "D942E66DD8C3F808DDD6FD11E64FE15B"
    # SK = "0F8509EB766B88C5F6E4B755BC2259EB"

    # app = Saturn(AK, SK, "https://s3.cn-global-0.xxyy.co:16000")

    # res = app.list_buckets('%Y-%m-%d %H:%M:%S')
    # print(res)

    # # res = app.list_objects('photo')
    # # print(res)
    # app.head_bucket('photo')
    # # app.head_bucket('photos')
    # # app.head_object("photo", "o47lzu6rqez11.jpg")
    # # app.get_object("photo", "o47lzu6rqez11.jpg")
    # app.get_bucket_acl("photo")

    # AK = "TLhVIrmQfleHqC4-MUPFXKeuVDxeDu3GTcdjBPB9"
    # SK = "qvHbBuGtpq065HaHP_Zah388qHoRzYHgfqxQAKLR"

    # app = Qiniu(AK, SK, "https://s3-us-north-1.qiniucs.com")
    # res = app.list_buckets('%Y-%m-%d %H:%M:%S')

    # res = app.get_bucket_acl('meetslut')
    # app.transfer(url, "meetslut")
    # res = app.list_objects('meetslut')
    # res = app.head_object('meetslut', '15922RankouRoom-01.jpg')
    # res = app.head_object('meetslut', 'icon.png')
    # app.download_file('meetslut', '15922RankouRoom-01.jpg', 'save.jpg')
    # app.upload_file("icon.png", 'meetslut', 'icon1.png')
    # res = app.head_object('meetslut', '15922RankouRoom-15.jpg')
    # res = app.delete_object('meetslut', '15922RankouRoom-15.jpg')
    # print(res)
    # body = app.get_object('meetslut', '15922RankouRoom-15.jpg')
    # with open("save.jpg", "wb") as f:
    #     f.write(body)

    # with open("icon.png", "rb") as f:
    #     body = f.read()
    # print(isinstance(body, bytes))
    # res = app.put_object("meetslut", "icon.png", body)
    # print(res)

    # import mimetypes

    # # print(mimetypes.guess_type("save.jpg"))
    # print(magic.from_file("save.jpg", mime=True))
    # print(magic.from_buffer(open("save.jpg", "rb").read(128), mime=True))

    url = "https://99zipai.com/d/file/selfies/202207/0bf581b1e6f551c4753c0ee8edc20faa.jpg"


    ApplicationKeyID = "004e1c16c97c6260000000002"    # AK
    ApplicationKey = "K004WTD5paSP5d6nxi+cR2FZDYx8fwg"    # SK
    EndpointURL = "https://s3.us-west-004.backblazeb2.com"

    app = BackBlaze(ApplicationKeyID, ApplicationKey, EndpointURL)
    res = app.list_buckets('%Y-%m-%d %H:%M:%S')
    print(res)

    res = app.get_bucket_acl('meetslut')
    print(res)

    app.transfer(url, 'meetslut')

# client = boto3.client(
#     's3',
#     aws_access_key_id = ApplicationKeyID,
#     aws_secret_access_key = ApplicationKey,
#     endpoint_url = "https://s3.us-west-004.backblazeb2.com"
# )
# r = client.list_buckets()
# print(r)
# print(f"{r['Owner']['DisplayName']}({r['Owner']['ID']})")
# buckets = r['Buckets']
# print(buckets)