import os
import sys
import argparse
import pathlib
import tempfile
import zipfile

import shapefile


def main(path, out_path, min_i, max_i):
    if not str(out_path).endswith(".zip"):
        raise ValueError("Le chemin de destination doit être un .zip.")
    sf = shapefile.Reader(path)
    out_tmp_dir = tempfile.mkdtemp()
    out = shapefile.Writer(os.path.join(out_tmp_dir, "carte_preco"))
    out.fields = sf.fields[1:]
    for i, rec in enumerate(sf.iterShapeRecords()):
        if min_i <= i <= max_i:
            out.record(*rec.record)
            out.shape(rec.shape)
    out.close()
    with zipfile.ZipFile(out_path, "w") as zipf:
        for filename in os.listdir(out_tmp_dir):
            if filename.startswith("carte_preco."):
                zipf.write(os.path.join(out_tmp_dir, filename), arcname=filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    parser.add_argument("min_i", type=int)
    parser.add_argument("max_i", type=int)
    args = parser.parse_args(sys.argv[1:])
    main(args.path, args.output, args.min_i, args.max_i)
