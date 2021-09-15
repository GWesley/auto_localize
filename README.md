# auto_localize
Auto generate iOS Localizable.strings for Xcode with google translate

# how to run
1. pip3 install googletrans
2. put origin Localizable.strings file in folder
3. python3 strings.py

# how to set origin languge
you can use `-o` to set your origin language,
for example `python3 strings.py -o fr`,
the default origin is english

# how to add more language
update LanguageCodes.txt to add or remove support languages
