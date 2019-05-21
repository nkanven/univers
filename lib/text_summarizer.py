from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from string import punctuation
from nltk.stem.snowball import SnowballStemmer
import nltk

class TextSummarizer:
     stemmer = SnowballStemmer("french")
     stopWords = set(stopwords.words("french") + list(punctuation))
     text = ""
     sentences = ""
     def tokenize_sentence(self):
          words = word_tokenize(self.text)
          print(words)
          return words

     def input_text(self, text):
          while True:
               self.text = text
               if(len(self.text) > 10):
                    break
               else:
                    print("Please input the text as length at least 10")

     
     def cal_freq(self, words):

          freqTable = dict()
          for word in words:
               word = word.lower()
               if word in self.stopWords:
                    continue
               
               if word in freqTable:
                    freqTable[word] += 1
               else:
                    freqTable[word] = 1
          return freqTable


     def compute_sentence(self,freqTable):
          
          self.sentences = sent_tokenize(self.text)
          sentenceValue = dict()

          for sentence in self.sentences:
               for index, wordValue in enumerate(freqTable, start=1):
                    if wordValue in sentence.lower():
                         if sentence in sentenceValue:
                              sentenceValue[sentence] += freqTable[wordValue]
                         else:
                              sentenceValue[sentence] = freqTable[wordValue]
          return sentenceValue
         
           

     def sumAvg(self,sentenceValue):
          sumValues = 0
          for sentence in sentenceValue:
               sumValues += sentenceValue[sentence]
          average = int(sumValues / len(sentenceValue))

          return average


     """def print_summary(self,sentenceValue,average):
          summary = ''
          adjuster = 1.5
          for sentence in self.sentences:
               if (sentence in sentenceValue) and (sentenceValue[sentence] > (adjuster * average)):
                    summary += " " + sentence

               if summary == "":
                    adjuster -= 0.1
               else:
                    break
          return summary"""
     
     def print_summary(self, sentenceValue, max_sentence):
          summary = ''
          tk = dict()
          for sentence in self.sentences:
               tk[sentenceValue[sentence]] = sentence
          
          for key in sorted(tk.keys(), reverse=True)[:max_sentence]:
               summary += tk[key]+"\n"
          
          return summary