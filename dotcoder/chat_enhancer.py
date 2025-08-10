class ChatEnhancer:
    def __init__(self, GEMINI_API_KEY=None):
        import os
        import google.generativeai as genai

        self.GEMINI_API_KEY = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Pass it as an argument or set it in environment variables.")

        genai.configure(api_key=self.GEMINI_API_KEY)
        self.genai = genai

    # ********** Gemini AI Interaction **********

    def _gemini_ai(self, messages: list, model: str = "gemini-1.5-flash", token: int = 6000, temperature: float = 0.7) -> str:
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"{role.capitalize()}: {content}\n"

        try:
            model_obj = self.genai.GenerativeModel(
                model_name=model,
                generation_config={
                    "temperature": temperature,
                    "top_p": 1.0,
                    "max_output_tokens": token,
                }
            )

            response = model_obj.generate_content(prompt)
            return response.text.strip() if response and hasattr(response, "text") else ""
        except Exception as e:
            return ""

    # ********** Conversation Summary **********

    def conversation_summary(self, conversation: list = []) -> str:
        if not conversation:
            return "No conversation to summarize."

        system_message = (
            "You are a highly intelligent and concise AI assistant. Your task is to read the following conversation between a human user and an AI assistant and summarize it clearly and accurately. "
            "Focus only on the key topic(s), goals, or problems discussed in the conversation. Ignore small talk and irrelevant details. "
            "Your response must be a concise and meaningful summary, without answering or continuing the conversation. "
            "Do not add greetings, opinions, or formatting. Return only the summary — no labels or prefixes."
        )

        conversation_text = ""
        for message in conversation:
            role = message.get("role", "user") if isinstance(message, dict) else "user"
            content = message.get("content", "") if isinstance(message, dict) else message
            conversation_text += f"{role} - {content}\n"

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": conversation_text}
        ]

        return self._gemini_ai(messages, model="gemini-1.5-flash", token=6000, temperature=0.7)

    # ********** Prompt Enhancement **********

    def enhance_prompt(self, prompt: str, conversation: list = []) -> str:
        conversation_summary = self.conversation_summary(conversation) if conversation else "No summary available."

        system_prompt = (
            "You are a prompt optimization assistant. Your task is to take the user's original prompt and make it clearer, more detailed, and more effective for an AI model to understand. "
            "If a summary of the prior conversation is provided, use it to improve context and add useful details, but do not answer the prompt. "
            "Only return the enhanced version of the prompt as a single sentence or paragraph. Do not include explanations or act like an assistant responding to the prompt."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Original Prompt: {prompt}"},
            {"role": "user", "content": f"Conversation Summary: {conversation_summary}"}
        ]

        return self._gemini_ai(messages, model="gemini-1.5-flash", token=1000, temperature=0.7)

