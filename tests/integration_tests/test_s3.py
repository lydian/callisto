def test_foo(s3, bucket):
    for key in s3.list_objects(Bucket=bucket)["Contents"]:
        print(key["Key"])
    assert False
