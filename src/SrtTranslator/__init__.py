import translators as ts
import json
import os
import enum
import time
import requests.exceptions

class SrtTranslator:
    def __init__(self, filename: str, source_lang: str = "en", target_lang: str = "tr", translator: callable = ts.translate_text, **translator_args) -> None:
        self.filename = filename
        if not os.path.isfile(self.filename):
            raise FileNotFoundError(f"{self.filename} is not exist!")
        self.filename_without_extension = os.path.splitext(self.filename)[0]
        self.translator = translator
        self.translator_args = translator_args
        if self.translator == ts.translate_text:
            self.translator_args = {
                "translator" : "modernMt", 
                "from_language" : source_lang, 
                "to_language" : target_lang,
                "update_session_after_freq" : 1000
            }

    def reader(self, is_write = False):
        class State(enum.Enum):
            NL = enum.auto()
            Number = enum.auto()
            Time = enum.auto()
            Text = enum.auto()
        
        subtitle = []
        with open(self.filename) as f:
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

        self.subtitle = subtitle
        
        if is_write:
            with open(f"{self.filename_without_extension}_reader.json", "w") as f:
                json.dump(subtitle, f, indent=4)

        return subtitle

    def preprocess_to_translator(self, is_write = False):
        
        Sentences = []
        sentence_finished = True
        block_index = -1
        carry_sentence = ""
        carry_block_index = 0
        carry_line_index = 0
        line_count_total = 0
        
        for i, block in enumerate(self.subtitle):
                
                for line_index,text in enumerate(block["Text"]):
                    
                    if sentence_finished:
                        Sentences.append({
                            "sentence": [],
                            "blocks": [],
                            "lines": [],
                            "line_count": []
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
                            line_count_total += 1
                    
                        
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
                        line_count_total += 1
                        
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
                            line_count_total += 1
                            Sentences[block_index]["line_count"].append(line_count_total)
                            line_count_total = 0
                        
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
                            
                            line_count_total += 1
                            Sentences[block_index]["line_count"].append(line_count_total)
                            line_count_total = 0       
                        
                        elif ques_mark and text.endswith("?"):
                            
                            if len(Sentences[block_index]["sentence"]) == 0:
                                
                                Sentences[block_index]["sentence"].append(text.strip())
                                Sentences[block_index]["blocks"].append(i)
                                Sentences[block_index]["blocks"].append(i)
                                Sentences[block_index]["lines"].append(line_index)
                                Sentences[block_index]["lines"].append(line_index)
                            
                            else:
                                
                                Sentences[block_index]['sentence'][0] = "".join(f"{Sentences[block_index]['sentence'][0]} {text}")
                                Sentences[block_index]["blocks"].append(i)
                                Sentences[block_index]["lines"].append(line_index)
                                
                            sentence_finished = True
                            line_count_total += 1
                            Sentences[block_index]["line_count"].append(line_count_total)
                            line_count_total = 0
                        
                        elif ques_mark != -1:
                            
                            two_sentences = text.split("?")
                            first_sentence = "".join(f"{two_sentences[0]}?")
                            carry_sentence = "".join(two_sentences[1] if len(two_sentences) > 1 else "")
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
                            
                            line_count_total += 1
                            Sentences[block_index]["line_count"].append(line_count_total)
                            line_count_total = 0
                            
                            sentence_finished = True            
                        
                        elif ex_mark and text.endswith("!"):
                            
                            if len(Sentences[block_index]["sentence"]) == 0:
                                
                                Sentences[block_index]["sentence"].append(text.strip())
                                Sentences[block_index]["blocks"].append(i)
                                Sentences[block_index]["blocks"].append(i)
                                Sentences[block_index]["lines"].append(line_index)
                                Sentences[block_index]["lines"].append(line_index)
                            
                            else:
                                
                                Sentences[block_index]['sentence'][0] = "".join(f"{Sentences[block_index]['sentence'][0]} {text}")
                                Sentences[block_index]["blocks"].append(i)
                                Sentences[block_index]["lines"].append(line_index)
                                
                            sentence_finished = True
                            line_count_total += 1
                            Sentences[block_index]["line_count"].append(line_count_total)
                            line_count_total = 0
                        
                        elif ex_mark != -1:
                            
                            two_sentences = text.split("?")
                            first_sentence = "".join(f"{two_sentences[0]}?")
                            carry_sentence = "".join(two_sentences[1] if len(two_sentences) > 1 else "")
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
                            line_count_total += 1
                            Sentences[block_index]["line_count"].append(line_count_total)
                            line_count_total = 0

        self.sentences = Sentences

        if is_write:        
            with open(f"{self.filename_without_extension}_sentences.json", "w") as f:
                json.dump(Sentences,f,indent=4)
                
        return self.sentences

    def translate(self, is_write = False):
        
        translated_json_file = []
        
        print("Translation will start! Please wait!")
            
        for index,block in enumerate(self.sentences):
            
            translated_json_file.append({
                "sentence": [],
                "blocks": [],
                "lines": [],
                "line_count": []
            })
            
            translated_json_file[index]["blocks"].append(block["blocks"])
            translated_json_file[index]["lines"].append(block["lines"])
            translated_json_file[index]["line_count"].append(block["line_count"])

            source_sentence = block["sentence"][0]            
            # result_translation = ts.translate_text(source_sentence,translator="modernMt", from_language="en", to_language="tr", update_session_after_freq = 1000)
            i = 3
            while i > 0:
                try:
                    result_translation = self.translator(source_sentence, **self.translator_args)
                    break
                except requests.exceptions.HTTPError:
                    time.sleep(5)
                    i -= 1
                    if i == 0:
                        raise requests.exceptions.HTTPError()
                    continue
            print(f"{index+1}. sentence is succesfully translated!")
            
            translated_json_file[index]["sentence"].append(result_translation)
        
        self.translated_sentences = translated_json_file

        if is_write:
            with open(f"{self.filename_without_extension}_translated_sentences.json", "w", encoding="utf-8") as translated_file:
                json.dump(translated_json_file,translated_file, indent=4, ensure_ascii=False)
        
        return self.translated_sentences

    def srt_creator(self):
        
        class State(enum.Enum):
            
            Null_State = enum.auto()
            Time_State = enum.auto()
            Text_State = enum.auto()
            Number_State = enum.auto()
            Same_Line_Sentence_Start = enum.auto()
            Continuous_Sentence = enum.auto()
        
        
        current_state = State.Number_State
        tf_index = 0 # translated_file_index_count
        check_continuity = False
        counter = 0
        from_continuous_condition = False
        
        with open(f"{self.filename_without_extension}_translated.srt", "w") as srt_file:
            
            current_end_block = self.translated_sentences[tf_index]["blocks"][0][1]
            current_end_line = self.translated_sentences[tf_index]["lines"][0][1]
            current_index_infos = [current_end_block, current_end_line]
            
            for reader_index,block in enumerate(self.subtitle):
                
                if current_state == State.Number_State:
                    
                    srt_file.writelines(f'{block["Number"]}\n')
                    current_state = State.Time_State

                if current_state == State.Time_State:
                    srt_file.writelines(f"{block['Time']}")
                    if check_continuity:
                        current_state = State.Continuous_Sentence
                    else:
                        current_state = State.Text_State
                
                if current_state == State.Continuous_Sentence:
                    
                    counter = step
                    updated_line_count = total_line_count - counter
                    current_block_line_count = len(block["Text"])
                    var_cblc_continuous = current_block_line_count
                    
                    if updated_line_count == 1:
                        
                        srt_file.writelines(f'\n{" ".join(word_list[-word_count_of_last_line:])}')
                        check_continuity = False
                        counter = 0
                        var_cblc_continuous -= 1
                        tf_index += 1
                    
                    elif updated_line_count >= 2:
                        
                        for i in range(counter,(counter + current_block_line_count)): # because word count of last line is calculated seperately.
                            
                            start = i * word_count_per_line
                            end = start + word_count_per_line
                            var_cblc_continuous -= 1
                            step += 1
                            
                            if i != total_line_count-1:
                                srt_file.writelines(f'\n{" ".join(word_list[start:end])}')
                                check_continuity = True
                            else:
                                srt_file.writelines(f'\n{" ".join(word_list[-word_count_of_last_line:])}')
                                check_continuity = False
                                counter = 0
                                tf_index += 1
                                break
                        
                    if var_cblc_continuous != 0:
                        current_state = State.Text_State
                        from_continuous_condition = True
                    else:
                        current_state = State.Null_State
                    
                if current_state == State.Text_State:
                    
                    block_is_not_finished = True # condition of the text state loop
                    current_block_line_count = len(block["Text"])
                    if from_continuous_condition == True:
                        var_cblc = var_cblc_continuous
                        from_continuous_condition = False
                    else:
                        var_cblc = current_block_line_count # backup variable of the line count that current block has.
                    step = 0 # line counter of current sentence for continuous_sentence state.
                    
                    while block_is_not_finished:
                        
                        next_start_block = self.translated_sentences[tf_index]["blocks"][0][0]
                        next_start_line = self.translated_sentences[tf_index]["lines"][0][0]
                        next_end_block = self.translated_sentences[tf_index]["blocks"][0][1]
                        next_end_line = self.translated_sentences[tf_index]["lines"][0][1]
                        next_start_index_infos = [next_start_block, next_start_line]
                        next_end_index_infos = [next_end_block, next_end_line]
                        first_line_condition = True
                        
                        word_list = self.translated_sentences[tf_index]["sentence"][0].split() # word list of the current sentence
                        
                        word_count_of_sentence = len(word_list) # word count of the sentence
                        total_line_count = self.translated_sentences[tf_index]["line_count"][0][0] # total line count of the current sentence

                        word_count_per_line = word_count_of_sentence // total_line_count # 15 // 4 = 3
                        word_count_of_last_line = word_count_per_line + (word_count_of_sentence % total_line_count) # 3 + (15 % 4) = 6
                        # That means there are 4 text lines that each has 3 words except last one. It has 6 words.

                        if ((word_count_of_sentence % total_line_count) > total_line_count - 2) and (total_line_count > 1):
                            new_div = word_count_of_last_line // total_line_count
                            new_car = word_count_of_last_line % total_line_count
                            word_count_per_line += new_div
                            word_count_of_last_line = new_div + new_car
                            # If word_count_per_line and word_count_last_line values does not evenly distributed, this condition would be active.
                            # It typically converts word distributions from (3,3,3,6) to (4,4,4,3) for distribute more evenly.
                            
                        if total_line_count == 1: # if the sentences distributed only one line
                            
                            if current_index_infos == next_start_index_infos and reader_index != 0:
                                srt_file.writelines(f' {self.translated_sentences[tf_index]["sentence"][0]}')
                                current_index_infos = next_start_index_infos
                                var_cblc += 1
                            else:
                                srt_file.writelines(f'\n{self.translated_sentences[tf_index]["sentence"][0]}')
                                
                            current_state = State.Null_State
                            var_cblc -= 1 # this variable decrased after each line is written. it used to check the condition that if current block is filled entirely.
                            tf_index += 1 # moving to the next sentence.
                        
                        elif total_line_count >= 2: # if the sentences distributed more than one line.
                            
                            val = total_line_count # backup of the total line count of the current sentence
                            current_block_line_count = val # update of the current block line count for the loop below.
                            for i in range(current_block_line_count): # because word count of last line is calculated seperately.
                                
                                start = i * word_count_per_line # start index to choose word range for the wordlist.
                                end = start + word_count_per_line # end index to choose word range for the wordlist.
                                val -= 1 # decreased for each iteration. checks rest of the line of current sentence.
                                var_cblc -= 1 # decreased after each line is written. checks rest of the line of current block.
                                step += 1 # calculates the written word iterations for will be used in continuous_sentence state.
                                
                                if val == 0: # if whole words were completely written except last part, write last line of the sentence.
                                    srt_file.writelines(f'\n{" ".join(word_list[-word_count_of_last_line:])}')
                                    check_continuity = False # not move to the state of continuous_sentence.
                                    step = 0
                                    
                                else: # if wordlist cannot be written to the lines in this iteration, write the range of the words and go to the continuous_sentence state to write rest of the sentences in the next block.
                                    if current_index_infos == next_start_index_infos and first_line_condition == True and reader_index != 0:
                                        srt_file.writelines(f' {" ".join(word_list[start:end])}')
                                        first_line_condition = False
                                        var_cblc += 1
                                    else:
                                        srt_file.writelines(f'\n{" ".join(word_list[start:end])}')
                                        
                                    check_continuity = True
                                    if var_cblc == 0: # if reached to the current block line count, break this iteration and go to the continuous_sentence state.
                                        break
                                
                                if check_continuity == False: # if current sentence is not continous, then move to the next sentence.
                                    tf_index += 1
                                    step = 0
                        if next_end_index_infos == next_start_index_infos:
                            current_index_infos = next_start_index_infos
                        else:
                            current_index_infos = next_end_index_infos        
                        if var_cblc < 1: # if reached to the current block line count, disband while loop.
                            block_is_not_finished = False
                        current_state = State.Null_State
                        
                if  current_state == State.Null_State:
                    srt_file.writelines("\n\n")
                    current_state = State.Number_State