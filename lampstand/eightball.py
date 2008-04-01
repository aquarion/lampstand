import random

def question():
	answers = (
		"As I see it, yes",
		"Ask again later",
		"Better not tell you now",
		"Cannot predict now",
		"Concentrate and ask again",
		"Don't count on it",
		"It is certain",
		"It is decidedly so",
		"Most likely",
		"My reply is no",
		"My sources say no",
		"Outlook good",
		"Outlook not so good",
		"Reply hazy, try again",
		"Signs point to yes",
		"Very doubtful",
		"Without a doubt",
		"Yes",
		"Yes - definitely",
		"You may rely on it",
		"Your answer lies within the catbus",
		"Only Legion can help you now",
		"The maelstrom deems it unlikely",
		"Transparent Electronic Envelopes. I think that means No",
		"Probably",
		"The internal kittens say 'No'. Also 'Keep Aestar Away From Us'",
		"Nonspecifically, yes",
		"YES! YES! A THOUSAND TIMES YES",
		"Not until you're all under my domain",
		"I shall not dignify your question with an answer",
		"No idea. Shall I phone a friend?",
		"Over my dead body",
		"Hah. No",
		"Hah. Yes"
		)
	
	return answers[(random.randint(0,len(answers)))]