import re
from sys import argv
from string import punctuation
from traceback import format_exc

class Logger:
    def __init__(self):
        print("Flushing initial logger")
        with open("runtime.log", "w") as f:
            f.write("")
    def error(self, message):
        print("Error, see log")
        with open("runtime.log", "a") as f:
            f.write("[Error]: " + message + "\n")
        exit(1)
    def info(self, message):
        with open("runtime.log", "a") as f:
            f.write("[Info]: " + message + "\n")

def tokenize_comment(cmt, st) -> str:
    if cmt in st:
        return st.split(cmt)[0]
    return st
def valid_comment(cmt) -> bool:
    for i in cmt:
        if i not in punctuation:
            return False
    return True

log = Logger()
log.info("Initial reading argv[1]")
if len(argv) < 2:
    log.error("Parameter minimal harus 2")

soalPattern = re.compile(r"^\d+\..*(\.{3}( +)?|=( +)?|\?( +)?|\!( +)?)$", re.IGNORECASE | re.MULTILINE)
jawabPattern = re.compile(r"^[a-d|A-D]*\.", re.IGNORECASE)

base_source = ""
out_soal = ""
out_jawab = ""
out_kunci = ""
segments = 3
segment_jawaban = 3
jawaban_counter = 3
comment_keyword = "//"

try:
    with open(argv[1]) as f:
        x = f.read().split("\n")
        if len(x) < 4:
            log.error("Length file {} harus 4".format(argv[1]))
        base_source = x[0].split("=")[1]
        out_soal = x[1].split("=")[1]
        out_jawab = x[2].split("=")[1]
        out_kunci = x[3].split("=")[1]
        if len(x) >= 5:
            gt = int(x[4].split("=")[1])
            segments = gt if gt >= 3 else 3
        if len(x) >= 6:
            dt_arg = x[5].split("=")[1].split(".")
            gt = int(dt_arg[0])
            gt1 = int(dt_arg[1])
            segment_jawaban = gt if gt >= 3 else 3
            jawaban_counter = gt1 if gt1 >= 3 else 3
        if len(x) >= 7:
            get_kw = x[6].split("=")[1]
            if not valid_comment(get_kw):
                log.error("Keyword untuk comment harus semuanya simbol (punctuation) keyword masukkan: {}".format(get_kw))
            comment_keyword = get_kw


except Exception as e:
    log.error("Python error: " + format_exc())

soal = []
jawab = []
kunci_jawab = []
log.info("Fetched output keywords (Reader: {}, Soal: {}, Jawaban: {}, Kunci: {})".format(base_source, out_soal, out_jawab, out_kunci))
log.info("Starting tool using soal segments of {} and jawaban segments of {}".format(segments, segment_jawaban))
log.info("Starting extraction")
with open(base_source, "r", encoding="utf-8") as f:
    s = ""
    try:
        s = f.read()
    except Exception as e:
        log.error("Python error: " + format_exc())
    pecahan = s.split("\n")
    st = ""
    kunci_jawaban = []
    detected_dash = False
    for idx in range(0, len(pecahan)):
        i = tokenize_comment(comment_keyword, pecahan[idx])
        if len(i) < 1:
            continue

        if i.lower() == "--kunci":
            log.info("Found kunci switch, clearing kunci fetch...")
            detected_dash = True
            break

        if i.lower().startswith("jawaban: a"):
            log.info("Fetched kunci jawaban A")
            continue
        elif i.lower().startswith("jawaban: b"):
            log.info("Fetched kunci jawaban B")
            continue
        elif i.lower().startswith("jawaban: c"):
            log.info("Fetched kunci jawaban C")
            continue
        elif i.lower().startswith("jawaban: d"):
            log.info("Fetched kunci jawaban D")
            continue

        is_soal = soalPattern.search(i) is not None
        is_jawaban = jawabPattern.search(i) is not None
        if not is_soal and not is_jawaban:
            st += i + "\n"
            log.info("Detected invalid soal, reading next input")
        
        if is_soal:
            log.info("Fetched soal")
            soal.append(i)
        
        if is_jawaban:
            log.info("Fetched Jawaban")
            jawab.append(i)
            if len(st) > 0:
                log.info("Found missing parts of soal")
                soal.append(st)
                st = ""

    # Fetch kunci jawaban (kalau ada)
    if not detected_dash:
        for i in pecahan:
            i = tokenize_comment(comment_keyword, i)
            if i.lower().startswith("jawaban: a"):
                kunci_jawaban.append(0)
            elif i.lower().startswith("jawaban: b"):
                kunci_jawaban.append(1)
            elif i.lower().startswith("jawaban: c"):
                kunci_jawaban.append(2)
            elif i.lower().startswith("jawaban: d"):
                kunci_jawaban.append(3)
            if len(kunci_jawaban) == segments:
                kunci_jawab.append(kunci_jawaban)
                kunci_jawaban = []
    else:
        yet_found = False
        log.info("Starting kunci switch extractor...")
        for i in pecahan:
            if yet_found:
                i = tokenize_comment(comment_keyword, i)
                if i.lower().startswith("a"):
                    log.info("Got A")
                    kunci_jawaban.append(0)
                elif i.lower().startswith("b"):
                    log.info("Got B")
                    kunci_jawaban.append(1)
                elif i.lower().startswith("c"):
                    log.info("Got C")
                    kunci_jawaban.append(2)
                elif i.lower().startswith("d"):
                    log.info("Got D")
                    kunci_jawaban.append(3)
                if len(kunci_jawaban) == segments:
                    kunci_jawab.append(kunci_jawaban)
                    kunci_jawaban = []
            if i.lower() == "--kunci":
                yet_found = True

log.info("Done got {} Soal, {} Jawaban, {} Kunci Jawab".format(len(soal), len(jawab), len(kunci_jawab)))
log.info("Preparing data...")
soal_len = len(soal)
remain = soal_len % segments

if soal_len < segments or remain != 0:
    log.error("Jumlah soal harus berbasis {}, Hanya terdapat {} soal, kurang {} soal lagi".format(segments, soal_len, segments - remain))

del soal_len
del remain

temp = jawab
jawab = []
jtmp = []

for i in range(0, 2):
    if i == 1:
        temp = jawab
        jawab = []
        jtmp = []
        for i in temp:
            jtmp.append(i)
            if len(jtmp) == segment_jawaban:
                jawab.append(jtmp)
                jtmp = []
    else:
        for i in temp:
            jtmp.append(i)
            if len(jtmp) == jawaban_counter:
                jawab.append(jtmp)
                jtmp = []
del temp
del jtmp

len_kunci = len(kunci_jawab)
len_soal = len(soal) / segments

if len_kunci != len_soal:
    if len_kunci > len_soal:
        log.error("Kunci jawaban melebihi soal segmen, harusnya terdapat {} kunci segmen, tetapi lebih {}."
        .format(len_soal, len_kunci - len_soal)
        + " (Segmen Kunci Jawaban: {}, Segmen Soal: {})".format(len_kunci, len_soal))
    else:
        log.error("Kunci jawaban kurang dari soal segmen, harusnya terdapat {} kunci segmen, tetapi kurang {}."
        .format(len_soal, len_soal - len_kunci)
        + " (Segmen Kunci Jawaban: {}, Segmen Soal: {})".format(len_kunci, len_soal))

del len_kunci
del len_soal

log.info("Writing to file...")
with open(out_soal, "w", encoding="utf-8") as f:
    counter = 1
    f.write("listOf(\n")
    try:
        for i in soal:
            if counter % segments == 0:
                if counter == len(soal):
                    f.write('Pair("""{}""", 0))'.format(i))
                else:
                    f.write('Pair("""{}""", 0)),\n\nlistOf('.format(i))
            else:
                f.write('Pair("""{}""", 0),\n'.format(i))

            counter += 1
    except Exception as e:
        log.error("Python error: " + format_exc())

with open(out_jawab, "w", encoding="utf-8") as f:
    len_jwb = len(jawab)
    f.write("listOf(\n")
    try:
        for i in range(0, len_jwb):
            f.write("listOf(")
            for x in range(0, len(jawab[i])):
                for j in range(0, len(jawab[i][x])):
                    if j == len(jawab[i][x])-1:
                        f.write('"{}"'.format(jawab[i][x][j]))
                    else:
                        f.write('"{}",'.format(jawab[i][x][j]))
                if x == len(jawab[i])-1:
                    f.write(")\n")
                else:
                    f.write("),\nlistOf(")    
            if i == len_jwb-1:
                f.write(")")
            else:
                f.write("),\nlistOf(\n")
    except Exception as e:
        log.error("Python error: " + format_exc())

with open(out_kunci, "w") as f:
    f.write("listOf(")
    jwb_k = len(kunci_jawab)
    for i in range(0, jwb_k):
        for j in range(0, len(kunci_jawab[i])):
            if j == len(kunci_jawab[i])-1:
                f.write("{}".format(kunci_jawab[i][j]))
            else:
                f.write("{},".format(kunci_jawab[i][j]))
        if i == jwb_k-1:
            f.write(")\n")
        else:
            f.write("),\nlistOf(")

log.info("Finished, exiting...")
