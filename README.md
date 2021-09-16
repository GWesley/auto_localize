# auto_localize
Auto translate Localizable.strings for multiple languages in Xcode

# Usage
1. pip3 install googletrans
2. put your origin Localizable.strings file in folder
3. python3 strings.py

![image](https://user-images.githubusercontent.com/2985638/133636085-7e3b7c1b-efcc-430a-a478-383ddd9e634f.png)


# how to set origin languge
you can use `-o` to set your origin language,

for example `python3 strings.py -o fr`,

the default origin is english

# how to add more language
update LanguageCodes.txt to add or remove support languages

