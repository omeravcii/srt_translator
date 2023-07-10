import translators as ts
import json
import os
import enum

def reader(filename):
    class State(enum.Enum):
        NL = enum.auto()
        Number = enum.auto()
        Time = enum.auto()
        Text = enum.auto()
    
    subtitle = []
    with open(filename) as f:
        count = -1
        state = State.Number
        for line in f.readlines():
            # print(line)
            if line.strip() == "":
                state = State.NL
                
            if state == State.NL:
                state = State.Number
                
            elif state == State.Number:
                subtitle.append({"Number": [],
                                "Time": [],
                                "Text": []
                                        })
                count += 1
                subtitle[count]["Number"] = line.strip()
                state = State.Time
                
            elif state == State.Time:
                subtitle[count]["Time"] = line.strip()
                state = State.Text
                
            elif state == State.Text:
                subtitle[count]["Text"].append(f"{line.strip()}")
                
    with open("reader_file_exp.json", "w") as f:
        json.dump(subtitle, f, indent=4)
    
    with open("reader_file_exp.json", "r") as f:
        file_into_subtitle_func = json.load(f)

    return file_into_subtitle_func

def preprocess_to_translator(subtitle):
    
    Sentences = []
    sentence_finished = True
    block_index = -1
    carry_sentence = ""
    carry_block_index = 0
    carry_line_index = 0
    
    for i, block in enumerate(subtitle):
            
            for line_index,text in enumerate(block["Text"]):
                
                if sentence_finished:
                    Sentences.append({
                        "sentence": [],
                        "blocks": [],
                        "lines": []
                    })
                    block_index += 1
                # print(text)
                
                    if len(carry_sentence) > 1:
                        
                        Sentences[block_index]["sentence"].append(carry_sentence.strip())
                        carry_sentence = ""
                        Sentences[block_index]["blocks"].append(carry_block_index)
                        carry_block_index = 0
                        Sentences[block_index]["lines"].append(carry_line_index)
                        carry_line_index = 0
                
                    
                dot = text.find(".")
                ques_mark = text.find("?")
                ex_mark = text.find("!")
                
                if dot == -1 and ques_mark == -1 and ex_mark == -1:
                    
                    sentence_finished = False
                    
                    if len(Sentences[block_index]["sentence"]) == 0:
                        
                        Sentences[block_index]["sentence"].append(text.strip())
                        Sentences[block_index]["blocks"].append(i)
                        Sentences[block_index]["lines"].append(line_index)
                    
                    else:
                        
                        Sentences[block_index]['sentence'][0] = "".join(f"{Sentences[block_index]['sentence'][0]} {text}")
                        # Sentences[block_index]["sentence"][0].join(text)
                   
                else:
                    
                    if dot and text.endswith("."):
                        
                        if len(Sentences[block_index]["sentence"]) == 0:
                            
                            Sentences[block_index]["sentence"].append(text.strip())
                            Sentences[block_index]["blocks"].append(i)
                            Sentences[block_index]["blocks"].append(i)
                            Sentences[block_index]["lines"].append(line_index)
                            Sentences[block_index]["lines"].append(line_index)
                            
                            sentence_finished = True
                        
                        else:
                            
                            Sentences[block_index]['sentence'][0] = "".join(f"{Sentences[block_index]['sentence'][0]} {text}")
                            Sentences[block_index]["blocks"].append(i)
                            Sentences[block_index]["lines"].append(line_index)
                            
                            sentence_finished = True
                    
                    elif dot != -1:
                        
                        two_sentences = text.split(".")
                        first_sentence = "".join(f"{two_sentences[0]}.")
                        carry_sentence = two_sentences[1]
                        carry_block_index = i
                        carry_line_index = line_index
                        
                        if len(Sentences[block_index]["sentence"]) == 0:
                            
                            Sentences[block_index]["sentence"].append(first_sentence.strip())
                            Sentences[block_index]["blocks"].append(i)
                            Sentences[block_index]["lines"].append(line_index)
                        else:
                            Sentences[block_index]['sentence'][0] = "".join(f"{Sentences[block_index]['sentence'][0]} {first_sentence}")
                            
                        Sentences[block_index]["blocks"].append(i)
                        Sentences[block_index]["lines"].append(line_index)
                        
                        sentence_finished = True        
                    
                    elif ques_mark and text.endswith("?"):
                        
                        if len(Sentences[block_index]["sentence"]) == 0:
                            
                            Sentences[block_index]["sentence"].append(text.strip())
                            Sentences[block_index]["blocks"].append(i)
                            Sentences[block_index]["blocks"].append(i)
                            Sentences[block_index]["lines"].append(line_index)
                            Sentences[block_index]["lines"].append(line_index)
                            
                            sentence_finished = True
                        
                        else:
                            
                            Sentences[block_index]['sentence'][0] = "".join(f"{Sentences[block_index]['sentence'][0]} {text}")
                            Sentences[block_index]["blocks"].append(i)
                            Sentences[block_index]["lines"].append(line_index)
                            
                            sentence_finished = True
                    
                    elif ques_mark != -1:
                        
                        two_sentences = text.split("?")
                        first_sentence = "".join(f"{two_sentences[0]}?")
                        carry_sentence = two_sentences[1]
                        carry_block_index = i
                        carry_line_index = line_index
                        
                        if len(Sentences[block_index]["sentence"]) == 0:
                            
                            Sentences[block_index]["sentence"].append(first_sentence.strip())
                            Sentences[block_index]["blocks"].append(i)
                            Sentences[block_index]["lines"].append(line_index)
                        else:
                            Sentences[block_index]['sentence'][0] = "".join(f"{Sentences[block_index]['sentence'][0]} {first_sentence}")
                            
                        Sentences[block_index]["blocks"].append(i)
                        Sentences[block_index]["lines"].append(line_index)
                        
                        sentence_finished = True            
                    
                    elif ex_mark and text.endswith("!"):
                        
                        if len(Sentences[block_index]["sentence"]) == 0:
                            
                            Sentences[block_index]["sentence"].append(text.strip())
                            Sentences[block_index]["blocks"].append(i)
                            Sentences[block_index]["blocks"].append(i)
                            Sentences[block_index]["lines"].append(line_index)
                            Sentences[block_index]["lines"].append(line_index)
                            
                            sentence_finished = True
                        
                        else:
                            
                            Sentences[block_index]['sentence'][0] = "".join(f"{Sentences[block_index]['sentence'][0]} {text}")
                            Sentences[block_index]["blocks"].append(i)
                            Sentences[block_index]["lines"].append(line_index)
                            
                            sentence_finished = True
                    
                    elif ex_mark != -1:
                        
                        two_sentences = text.split("?")
                        first_sentence = "".join(f"{two_sentences[0]}?")
                        carry_sentence = two_sentences[1]
                        carry_block_index = i
                        carry_line_index = line_index
                        
                        if len(Sentences[block_index]["sentence"]) == 0:
                            
                            Sentences[block_index]["sentence"].append(first_sentence.strip())
                            Sentences[block_index]["blocks"].append(i)
                            Sentences[block_index]["lines"].append(line_index)
                        else:
                            
                            Sentences[block_index]['sentence'][0] = "".join(f"{Sentences[block_index]['sentence'][0]} {first_sentence}")
                            
                        Sentences[block_index]["blocks"].append(i)
                        Sentences[block_index]["lines"].append(line_index)
                        
                        sentence_finished = True

                    
                    
    with open("text_to_translator.json", "w") as f:
        json.dump(Sentences,f,indent=4)
    
    with open("text_to_translator.json", "r") as f:
        text_to_translator = json.load(f)
            
    return text_to_translator
    

def translator(subtitle):
    
    char_count = 0
    step_count = 1
    index_count = 0
    i_counter = -1
    condition = True
    
    while condition:
        
        with open(f"to_translator_{step_count}.txt", "w") as f:

            for block in subtitle[index_count:]:
                
                i_counter += 1
                
                if len(block["sentence"]) == 1:
                    text = block["sentence"][0]
                    f.writelines(f'{text}\n\n')
                    
                    char_count += len(text)
                    
                    
                    if char_count > 4000:
                        
                        char_count = 0
                        step_count += 1
                        index_count = i_counter + 1
                        break
        
        if i_counter + 1 == len(subtitle):
            condition = False
            
    with open("translated_file.txt", "a") as t_file:
        
        for file_number in range(1,step_count+1):
            
            with open(f"to_translator_{file_number}.txt", "r") as f:
                
                print(f"Document {file_number} translation process has started. Please wait till the end.")
                translated = ts.translate_text(f.read(), translator="modernMt", from_language="en", to_language="tr")
                
            t_file.write(translated.values)
            # os.remove(f"to_translator_{file_number}.txt")
            
    path = "translated_file.txt"
    return path

def translator_2(subtitle):
    
    translated_json_file = []
    
    print("Translation will start! Please wait!")
    
    with open("translated_file3.json", "w", encoding="utf-8") as translated_file:
        
        for index,block in enumerate(subtitle):
            
            translated_json_file.append({
                "sentence": [],
                "blocks": [],
                "lines": []
            })
            
            translated_json_file[index]["blocks"].append(block["blocks"])
            translated_json_file[index]["lines"].append(block["lines"])

            source_sentence = block["sentence"][0]            
            result_translation = ts.translate_text(source_sentence,translator="modernMt", from_language="en", to_language="tr", update_session_after_freq = 10)
            print(f"{index+1}. sentence is succesfully translated!")
            
            translated_json_file[index]["sentence"].append(result_translation)
            
        json.dump(translated_json_file,translated_file, indent=4, ensure_ascii=False)







def srt_creator(translated_file, reader_file):
    
    class State(enum.Enum):
        
        Null_State = enum.auto()
        Time_State = enum.auto()
        Text_State = enum.auto()
        Number_State = enum.auto()
        Same_Line_Sentence_Start = enum.auto()
        Continuous_Sentence = enum.auto()
    
    
    current_state = State.Number_State
    tf_index = 0 # translated_file_index_count
    check_start = False
    check_continuity = False
    counter = 0
    
    with open(translated_file, "r") as translated_file:
        
        tf = json.load(translated_file)
        
        with open(reader_file, "r") as reader_file:
            
            rf = json.load(reader_file)   
        
            with open("translated_subtitle.srt", "a") as srt_file:
                
                for reader_index,block in enumerate(rf):
                    
                    if current_state == State.Number_State:
                        
                        srt_file.writelines(f'{block["Number"]}\n')
                        current_state = State.Time_State

                    
                    if current_state == State.Time_State:
                        srt_file.writelines(f"{block['Time']}\n")
                        if check_start:
                            current_state = State.Same_Line_Sentence_Start
                        if check_continuity:
                            current_state = State.Continuous_Sentence
                        else:
                            current_state = State.Text_State
                    
                    if current_state == State.Same_Line_Sentence_Start:
                        None
                    
                    if current_state == State.Continuous_Sentence:
                        
                        counter += 2
                        new_line_count = total_line_count - counter
                        
                        if new_line_count == 1:
                            
                            srt_file.writelines(f'{" ".join(word_list[-word_count_of_last_line:])}\n')
                            check_continuity = False
                            counter = 0
                            tf_index += 1
                        
                        elif new_line_count >= 2:
                            
                            for i in range(counter,counter+2): # because word count of last line is calculated seperately.
                                
                                start = i * word_count_per_line
                                end = start + word_count_per_line
                                
                                if i != total_line_count-1:
                                    srt_file.writelines(f'{" ".join(word_list[start:end])}\n')
                                    check_continuity = True
                                else:
                                    srt_file.writelines(f'{" ".join(word_list[-word_count_of_last_line:])}\n')
                                    check_continuity = False
                                    counter = 0
                                    tf_index += 1
                                    break
                            
                        current_state = State.Null_State
                        
                    if current_state == State.Text_State:
                        
                        word_list = tf[tf_index]["sentence"][0].split()
                        
                        word_count_of_sentence = len(word_list)
                        
                        block_start = tf[tf_index]["blocks"][0][0] # example = 10
                        block_end = tf[tf_index]["blocks"][0][1]   # example = 11
                        line_start = tf[tf_index]["lines"][0][0]   # example = 0
                        line_end = tf[tf_index]["lines"][0][1]     # example = 1
                        
                        if line_end == line_start:
                            total_line_count = ((block_end - block_start) * 2) + 1 
                            
                        elif line_end > line_start:
                            total_line_count = ((block_end - block_start) * 2) + 2 # example total line = 4
                            
                        elif line_end < line_start:
                            total_line_count = ((block_end - block_start) * 2)
                        
                        word_count_per_line = word_count_of_sentence // total_line_count # 15 // 4 = 3
                        word_count_of_last_line = word_count_per_line + (word_count_of_sentence % total_line_count) # 3 + (15 % 4) = 6
                        
                        # That means there are 4 text lines that each has 3 words except last one. It has 6 words.
                       
                        if total_line_count == 1:
                            
                            srt_file.writelines(f'{tf[tf_index]["sentence"][0]}\n')
                            current_state = State.Null_State
                            tf_index += 1
                        
                        elif total_line_count == 2:
                            
                            srt_file.writelines(f'{" ".join(word_list[:word_count_per_line])}\n')
                            srt_file.writelines(f'{" ".join(word_list[-word_count_of_last_line:])}\n')
                            current_state = State.Null_State
                            tf_index += 1
                        
                        elif total_line_count > 2:
                            
                            for i in range(2): # because word count of last line is calculated seperately.
                                
                                start = i * word_count_per_line
                                end = start + word_count_per_line
                                
                                srt_file.writelines(f'{" ".join(word_list[start:end])}\n')
                                
                                check_continuity = True
                                current_state = State.Null_State
                       
                    if  current_state == State.Null_State:
                        srt_file.writelines("\n")
                        current_state = State.Number_State





def srt_creator_yedek(translated_file, reader_file):
    
    class State(enum.Enum):
        
        Null_State = enum.auto()
        Time_State = enum.auto()
        Text_State = enum.auto()
        Number_State = enum.auto()
        
    current_state = State.Number_State
    reader_index = 0
    
    with open(translated_file, "r") as translated_file:
        
        tf = json.load(translated_file)

        with open(reader_file, "r") as reader_file:
            
            rf = json.load(reader_file)
            
            with open("result_file.srt", "a") as result:
                
                for index,block in enumerate(tf):
                    
                    if current_state == State.Number_State:
                        result.writelines(f'{rf[reader_index]["Number"]}\n')
                        current_state = State.Time_State
                                            
                    if current_state == State.Time_State:
                        result.writelines(f'{rf[reader_index]["Time"]}\n')
                        current_state = State.Text_State
                    
                    if current_state == State.Text_State:
                        
                        word_list = block["sentence"][0].split()
                        word_count_of_sentence = len(word_list) # example count = 15
                        
                        block_start = block["blocks"][0][0] # example = 10
                        block_end = block["blocks"][0][1]   # example = 11
                        line_start = block["lines"][0][0]   # example = 0
                        line_end = block["lines"][0][1]     # example = 1
                        
                        if line_end == line_start:
                            total_line_count = ((block_end - block_start) * 2) + 1 
                            
                        elif line_end > line_start:
                            total_line_count = ((block_end - block_start) * 2) + 2 # example total line = 4
                            
                        elif line_end < line_start:
                            total_line_count = ((block_end - block_start) * 2)
                        
                        word_count_per_line = word_count_of_sentence // total_line_count # 15 // 4 = 3
                        word_count_of_last_line = word_count_per_line + (word_count_of_sentence % total_line_count) # 3 + (15 % 4) = 6
                        
                        # That means there are 4 text lines that each has 3 words except last one. It has 6 words.
                        
                        if total_line_count == 1:
                            
                            result.writelines(f'{block["sentence"][0]}\n')
                            current_state = State.Null_State
                        
                        elif total_line_count == 2:
                            
                            result.writelines(f'{" ".join(word_list[:word_count_per_line])}\n')
                            result.writelines(f'{" ".join(word_list[-word_count_of_last_line:])}\n')
                            current_state = State.Null_State
                        
                        elif total_line_count > 2:
                            
                            for i in range(total_line_count-1): # because word count of last line is calculated seperately.
                                
                                start = i * word_count_per_line
                                end = start + word_count_per_line
                                
                                result.writelines(f'{" ".join(word_list[start:end])}\n')

                    if current_state == State.Null_State:
                        result.writelines("\n")
                        current_state = State.Number_State
                        reader_index += 1
                        
                    
                
                
            



example_subtitle = "example_sub.srt"
subtitle_file_original = "What.Is.A.Woman.English-WWW.MY-SUBS.CO.srt"

file_into_subtitle_func = reader(subtitle_file_original)

text_to_translator = preprocess_to_translator(file_into_subtitle_func)

# translated_file = translator(text_to_translator)
translated_file2 = translator_2(text_to_translator)

# translated_file = "translated_file2.json"

# srt_creator(translated_file=translated_file,reader_file="reader_file_exp.json")


