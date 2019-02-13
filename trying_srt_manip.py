srt_dictionary = {}

with open("C:/Users/chriss/Downloads/C1E001_FINAL.srt", 'r', encoding='utf-8') as srt:


  time = ""
  text = ""

  for i, line in enumerate(srt):
    x = i+1
    if x % 4 == 2:
      time = line.split('-->')[0]
      print(str(x)+" - "+time)
    elif x % 4 == 3:
      text = line
      print(str(x)+" - "+text)
    elif x % 4 == 0:
      srt_dictionary[time] = text.replace('\n','')
      time = ""
      text = ""

print(srt_dictionary)

