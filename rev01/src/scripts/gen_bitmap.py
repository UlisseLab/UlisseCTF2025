from sys import argv, stdout
import os

bm_map = {}


with open("resources/bitmaps.csv", "r") as f:
    """Parse bitmaps file and associate each letter to its own bitmap"""
    for line in f:
        bitmap, letter = line.rstrip("\n").split("; ")
        bm_map[letter] = bitmap.split(",")

flag = os.getenv("FLAG")
if flag is None:
    print("No flag found in env")
    exit(1)

if len(argv) < 2:
    dst_file = stdout
else:
    dst_file = open(argv[1], "w")

bitmap_code = "\n".join(map(lambda c: f"\t/* '{c}' */ {{0x{', 0x'.join(bm_map[c])}}},", flag))
dst_file.write(
    f"""/** This file was generated automatically */
#include <inttypes.h>
#define FLAG "{flag}"
#define FLAG_LEN (sizeof FLAG)

#define BITMAP_H 16
#define BITMAP_W 12

const uint16_t bitmap[][BITMAP_H] = {{
{bitmap_code}
}};
"""
)
dst_file.close()
