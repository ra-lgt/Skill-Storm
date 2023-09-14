

class Cyberbullying:
	bad_words=[]

	def __init__(self):
		
		file_path = 'bad_words_all.txt'
		with open(file_path, 'r') as file:
			for line in file:
				words = line.split()
				for word in words:
					self.bad_words.append(word.strip())
		

	def check_bad_words(self,message):
		data=message.split(":")

		for i in range(1,len(data)):
			

			

			if(data[i].strip() in self.bad_words):

				return True
		return False




