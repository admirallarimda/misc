#!/usr/bin/python

import os
import os.path
import datetime
import shutil
import getopt
import sys
import PIL.Image, PIL.ExifTags

_DateTag = "DateTimeOriginal"


def find_jpg_with_creation_date(folder, date_from, date_to):
    result = []
    for root, dirnames, filenames in os.walk(folder):
        for f in filenames:
            if not (f.endswith("jpg") or f.endswith("jpeg")):
                continue
            fpath = os.path.join(root, f)
            try:
                img = PIL.Image.open(fpath)
                if img.format != "JPEG":
                    print "Unsupported img format {}  at '{}'".format(img.format, fpath)
                    continue
                exifdata = img._getexif()
                if exifdata is None:
                    continue
                exif = {
                    PIL.ExifTags.TAGS[k]: v
                    for k, v in exifdata.items()
                    if k in PIL.ExifTags.TAGS
                }
                if _DateTag not in exif:
                    print "No {} tag in exif for file at '{}'".format(_DateTag, fpath)
                    continue
                exif_date_str = exif[_DateTag]
                exif_date = datetime.datetime.strptime(exif_date_str, "%Y:%m:%d %H:%M:%S")
                if exif_date >= date_from and exif_date < date_to:
                    print "Found suitable file at '{}' with date {}".format(fpath, exif_date)
                    result.append(fpath)

            except Exception as e:
                print "Exception caught: {}".format(e)
                continue

    return result


def copy_found(files, dstdir):
    for f in files:
        topath = os.path.join(dstdir, f)
        print "Copying {} to {}".format(f, topath)
        dirpath = os.path.dirname(topath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        shutil.copyfile(f, topath)


def main():
    srcdir = ""
    dstdir = "./jpg_found"
    date_from = datetime.datetime(1970, 1, 1)
    date_to = datetime.datetime(2100, 12, 31)

    opts, args = getopt.getopt(sys.argv[1:], "", ["src=", "dst=", "datefrom=", "dateto="])
    for opt, val in opts:
        if opt == "--src":
            srcdir = val
        elif opt == "--dst":
            dstdir = val
        elif opt == "--datefrom":
            date_from = datetime.datetime.strptime(val, "%Y-%m-%d")
        elif opt == "--dateto":
            date_to = datetime.datetime.strptime(val, "%Y-%m-%d")

    if srcdir == "":
        print "Missing argument with src folder"
        return 1

    files = find_jpg_with_creation_date(srcdir, date_from, date_to)
    print "Found {} files".format(len(files))
    copy_found(files, dstdir)


if __name__ == "__main__":
    main()
