def analyze_string(s):
    elements = s.split()
    print(elements)
    unique_elements = set(elements)
    
    if len(unique_elements) > 2:
        print("超過兩種不同的元素，程式結束")
        return

    # 轉換元素為0和1
    element_map = {element: idx for idx, element in enumerate(unique_elements)}
    transformed_elements = [str(element_map[element]) for element in elements]

    # 將轉換後的元素拼接成字串
    transformed_string = ''.join(transformed_elements)
    print(transformed_string)
    print(int(transformed_string, 2))

# 字串範例
s = "1 0 3"

analyze_string(s)