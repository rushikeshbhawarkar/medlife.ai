# # Purpose: Offline, clearly labelled sample health answers; requires no API key.
# # Edit these canned responses for local end-to-end demos.
# import re
# from .base import AIProvider

# class MockProvider(AIProvider):
#     def answer(self, query: str) -> str:
#         q = query.lower()
#         if re.search(r"a1c|sugar|diabet|glucose", q):
#             answer = "**Sample guidance: understanding A1C**\n- A1C is one measure of average blood glucose over time.\n- A clinician can interpret the result with your history and other tests.\n- Balanced meals and regular activity may support glucose health."
#         elif re.search(r"pressure|hypertens|\bbp\b", q):
#             answer = "**Sample guidance: blood pressure**\n- Take readings while seated and rested, and record them.\n- Discuss repeated high readings with a clinician.\n- Seek urgent help for a very high reading with chest pain, breathing difficulty, weakness, or confusion."
#         elif re.search(r"medicine|tablet|drug|side effect|dose", q):
#             answer = "**Sample guidance: medicine safety**\n- Follow the instructions provided by your prescriber and medicine label.\n- Do not start, stop, or change a prescribed medicine based only on chat advice.\n- Ask a pharmacist or clinician about interactions or side effects."
#         else:
#             answer = "**Sample general health guidance**\nI can share general information, but this sample response is not a medical assessment. A healthcare professional can advise based on the person's full history."
#         return answer + "\n\nThis is a mock-provider sample, not a diagnosis or a substitute for professional medical advice."





# Purpose: Offline, clearly labelled sample health answers; requires no API key.
# Edit these canned responses for local end-to-end demos.
import re
from .base import AIProvider

class MockProvider(AIProvider):
    def answer(self, query: str, context: str = "") -> str:
        q = query.lower()
        if re.search(r"a1c|sugar|diabet|glucose", q):
            answer = "**Sample guidance: understanding A1C**\n- A1C is one measure of average blood glucose over time.\n- A clinician can interpret the result with your history and other tests.\n- Balanced meals and regular activity may support glucose health."
        elif re.search(r"pressure|hypertens|\bbp\b", q):
            answer = "**Sample guidance: blood pressure**\n- Take readings while seated and rested, and record them.\n- Discuss repeated high readings with a clinician.\n- Seek urgent help for a very high reading with chest pain, breathing difficulty, weakness, or confusion."
        elif re.search(r"medicine|tablet|drug|side effect|dose", q):
            answer = "**Sample guidance: medicine safety**\n- Follow the instructions provided by your prescriber and medicine label.\n- Do not start, stop, or change a prescribed medicine based only on chat advice.\n- Ask a pharmacist or clinician about interactions or side effects."
        else:
            answer = "**Sample general health guidance**\nI can share general information, but this sample response is not a medical assessment. A healthcare professional can advise based on the person's full history."
        suffix = "\n\nThis is a mock-provider sample, not a diagnosis or a substitute for professional medical advice."
        if context:
            suffix += " The selected member profile was loaded, but the mock provider does not interpret profile data. Configure a real AI provider for personalized responses."
        return answer + suffix
