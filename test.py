
a = [4,5,3,5,0,0,0,5,4,4,5,4,5,6,3,0,0,0,4,3,4,6,7,5,4,4,3,3,3,2,2,2,4,5]

def find_chunks(input_list):
    result_list = []
    section = {}
    count = 0
    for i in xrange(0,len(input_list)-1):
        if count > 0:
            section[input_list[i]] = count
        if input_list[i] == input_list[i+1]:
            count = count + 1
        else:
            count = 0
            result_list.append(section)
            section = {}
    return result_list


print find_chunks(a)

