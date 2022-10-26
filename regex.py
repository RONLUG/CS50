import re

link="https://www.youtube.com/watch?somethingherev=sa-TUpSx1JA"
match = re.search(r"(https?://)?(www\.)?(youtube\.com/watch\?).*v=(.+?)(&|$)", link)


if match == None:
    print("Not A Youtube Link")
else:
    print("Is an youtube link")
    print(match)
    print(match[0])
    print(match[3])
    print(match[4])

# import re

# target_string = "The price of PINEAPPLE ice cream is 20"

# # two groups enclosed in separate ( and ) bracket
# result = re.search(r"(\b[A-Z]+\b).+(\b\d+)", target_string)

# print(result)

# # Extract matching values of all groups
# print(result.groups())
# # Output ('PINEAPPLE', '20')

# # Extract match value of group 1
# print(result.group(1))
# # Output 'PINEAPPLE'

# # Extract match value of group 2
# print(result.group(2))
# # Output 20