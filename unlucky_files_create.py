input_txt = 'unlucky input.txt'
with open(input_txt) as f:
    allLines = f.readlines()
print('Read', len(allLines), 'lines from',)

lineIndex_total = 1
lineIndex_single = 1
fileIndex = 1
while lineIndex_total <= len(allLines):
    fileName = 'Data' + str(fileIndex) + '.txt'
    with open(fileName, 'w') as fileWrite:
        print(fileName)
        # fileWrite.write('-'.join([str(lineIndex_total), fileName]))
        while lineIndex_single <= 40:
            # print(lineIndex_total, lineIndex_single)
            try:
                line = allLines[lineIndex_total - 1]
            except IndexError:
                print('Something wrong at lineIndex_total=', lineIndex_total)
            fileWrite.write(line)
            lineIndex_total += 1
            lineIndex_single += 1
        lineIndex_single = 1
    fileIndex += 1
