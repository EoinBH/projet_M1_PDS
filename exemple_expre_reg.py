import re

texte = "Lorem ipsum dolor sit amet, consectetur adipiscing elit," \
"sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." \
"Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut" \
"aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in" \
"voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint" \
"occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit" \
"anim id est laborum."

motif = re.compile("Duis")
matches = motif.finditer(texte)
for m in matches :
    print(f"Motif trouvé: {m.group()}, start : {m.start()}, end : {m.end()}")