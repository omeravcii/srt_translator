from . import SrtTranslator
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = "SrtTranslator", 
        usage = "Just give a filename",
        description = "Translates your subtitles"
    )
    parser.add_argument("filename", help = "Input file name")
    parser.add_argument("-s", "--source_lang", default = "en", help = "Source language")
    parser.add_argument("-t", "--target_lang", default = "tr", help = "Target language")

    args = parser.parse_args()

    translator = SrtTranslator(args.filename, source_lang = args.source_lang, target_lang = args.target_lang)
    translator.reader(True)
    translator.preprocess_to_translator(True)
    translator.translate(True)
    translator.srt_creator()