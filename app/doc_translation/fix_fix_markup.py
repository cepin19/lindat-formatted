import sys
import re
tr=re.compile(r"</?(g|x|bx|ex|lb|mrk).*?>")
for line in sys.stdin:

    line_raw,line_xliff=line.split('\t')
    new_line_xliff=""
    #print(line_raw)
    #print(line_xliff)
    tags=tr.finditer(line_xliff)
    intervals=[(t.start(),t.end()) for t in tags]
    covered_raw_i=-1
    #print(intervals)
    for i,char in enumerate(list(line_xliff)):
        #new_line_xliff += char
        #continue
        #   print(i)
        if any(i in range(interval[0], interval[1]-1) for interval in intervals):
         # print(i)
            new_line_xliff += char
            continue
        if char.isspace():

            if len(line_raw)<=covered_raw_i+1:
                new_line_xliff+=char
                continue
            #print("found space at {}, covered {} in orig, next orig char is: {}".format(new_line_xliff,line_raw[:covered_raw_i],line_raw[covered_raw_i+1]))
            if line_raw[covered_raw_i+1].isspace():#detokenize, e.g. produce space only when there was a space in raw translation doc
                new_line_xliff+=char
            continue

        prev_ci=covered_raw_i
        covered_raw_i=line_raw.find(char,covered_raw_i+1)
        if covered_raw_i==-1:#shouldn't happend
            covered_raw_i=prev_ci
        #p#rint("char: {}, ci: {}".format(char,covered_raw_i))
        if covered_raw_i-prev_ci>1 and line_raw[covered_raw_i-1].isspace() and  not line_xliff[i-1].isspace():
            new_line_xliff+=" "

            found_char=line_raw[covered_raw_i]
     #       print("found "+found_char+ " at pos "+ str(covered_raw_i) +" for "+ char + " at pos " + str(i))
            # actually i can even detokenize the text back into the orginal form from the model with this

        new_line_xliff += char
    print(new_line_xliff,end='')
