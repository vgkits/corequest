def webSequenceAdaptor(createChoiceRoutine):
    consolePrint = print
    def createSequence(print):
        sack = {}  #create empty inventory
        choiceRoutine = createChoiceRoutine(print, sack)
        try:
            clickedChoice = None
            while True:
                # send previous choice, retrieve the next set of choices
                choices = choiceRoutine.send(clickedChoice)
                if choices is not None:
                    for choiceIndex,choiceText in enumerate(choices):
                        print(
                            b"<form method='post' style='display: inline;' ><input type='hidden' name='response' value='",
                            str(choiceIndex) ,
                            b"'><button type='submit'>",
                            choiceText ,b"</button></form>"
                        )
                    clickedResponse = yield None
                    try:
                        clickedChoice = choices[int(clickedResponse)]
                        continue
                    except Exception as e: # Response was non-numeric
                        consolePrint(e)
                        pass
                yield None
                clickedChoice = None
        except StopIteration:
            return
    return createSequence


def textSequenceAdaptor(createChoiceRoutine):
    consolePrint = print
    def createSequence(print):
        sack = {}  #create empty inventory
        choiceRoutine = createChoiceRoutine(print, sack)
        try:
            typedChoice = None
            while True:
                # send previous choice, retrieve the next set of choices
                choices = choiceRoutine.send(typedChoice)
                if choices is not None:
                    for choiceIndex,choiceText in enumerate(choices):
                        print(str(choiceIndex), ") ", choiceText)
                    typedResponse = yield "Enter your choice: "
                    try:
                        typedIndex = int( typedResponse )
                        typedChoice = choices[typedIndex]
                        continue
                    except Exception as e:
                        consolePrint(e)
                        pass
                        # todo handle non-numeric by trying to find text in lowercase-matched choiceText
                typedChoice = None
                yield "Press Enter to continue... "

        except StopIteration:
            return
    return createSequence
