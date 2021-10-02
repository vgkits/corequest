def createRootGenerator():
    yield "Alpha"
    yield from createBetaGenerator()
    yield "Delta"


def createBetaGenerator():
    yield "Beta"
    return "Gamma"
