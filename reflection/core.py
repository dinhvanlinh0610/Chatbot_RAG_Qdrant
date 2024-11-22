import google.generativeai as genai


class Reflection():
    
    def __init__(self, llm):
        self.llm = llm

    def _concat_and_format_texts(self, data):
        concatenatedTexts = []
        for entry in data:
            role = entry.get('role', '')
            all_texts = ' '.join([part['text'] for part in entry['parts']])
            concatenatedTexts.append(f"{role}: {all_texts} \n")

        return ''.join(concatenatedTexts)
    
    def __call__(self, chatHistory, lastItemsConsidereds=100):

        if len(chatHistory) >= lastItemsConsidereds:
            chatHistory = chatHistory[len(chatHistory) - lastItemsConsidereds:]

        historyString = self._concat_and_format_texts(chatHistory)

        print("historyString", historyString, "\n-----------------------------------------------\n") 

        #higherLevelSummariesPrompt = """Tôi sẽ cung cấp cho bạn một lịch sử hội thoại. Nhiệm vụ của bạn là xác định câu hỏi cuối cùng mà người dùng đang thực sự muốn hỏi và tổng hợp nó thành một câu hỏi gọn gàng, chính xác dựa trên toàn bộ ngữ cảnh của cuộc hội thoại\n. {historyString}
        #""".format(historyString=historyString)
        higherLevelSummariesPrompt = """Bạn là một chuyên gia về luật hôn nhân và gia đình Việt Nam. Xin vui lòng cho tôi biết số chương, mục và tên điều trong Luật Hôn nhân và Gia đình Việt Nam năm 2014 để có thể giải quyết vấn đề trong đoạn hội thoại. 
        Đoạn hội thoại : "\n. 
        "{historyString}" .\n 
        Không đưa ra bất kỳ thông tin nào khác ngoài số chương, mục, và tên điều . 
        Ví dụ "Chương III Mục 3 Điều 50. Thỏa thuận về chế độ tài sản của vợ chồng bị vô hiệu".
        """.format(historyString=historyString)

        # print(higherLevelSummariesPrompt)

        #dùng llm để generate content với gemini-1.5pro
        respone = self.llm.generate_content(higherLevelSummariesPrompt)

        return respone.text

