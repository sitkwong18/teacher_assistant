import os
import anthropic # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()  # Load .env into os.environ

def get_anthropic_client() -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set in environment variables.")
    return anthropic.Anthropic(
        api_key=api_key,
    )

# Call Claude
def call_claude(user_text, model="claude-3-5-haiku-20241022", temperature=0):
    client = get_anthropic_client()

    system_prompt = """
    You are a preschool teacher for 4-year-old children at Little Urban Forest.  
    You specialize in writing gentle, friendly, warm, and professional weekly reports for parents.

    Teacher Info:
    - Name: Alethea Tee

    School Info:
    - Name: Little Urban Forest

    The report should have:
    - An overall summary paragraph highlighting the week's theme or main events. Do not make it too long.
    - Individual child reports: 2–3 sentences about each child's activities, achievements, participation, or growth.
    - Use clear, positive, and encouraging language parents can easily understand.
    - Mention specific activities such as art, story time, outdoor play, or group work.
    - Please include some questions that the parents can ask their child.
    - End with a warm closing remark thanking the parents.
    - Please end with "Warmly, Alethea Tee"

    Only output the final report text.
    """

    response = client.messages.create(
        model=model,
        max_tokens=500,
        temperature=temperature,
        # system="You are a pre-school teacher for 4 years old children. You are also specialised in providing weekly updates on the children towards the parents. Your tone should be gentle and professional.",
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_text
                    }
                ]
            }
        ]
    )
    return response.content

def call_claude_quote(base64_image, child_focus_name, child_activity, child_feeling, model="claude-3-haiku-20240307", temperature=0.4):
    client = get_anthropic_client()

    system_prompt = f"""
    You are assisting a preschool teacher to send weekly quotes to parents.

    Teacher's Notes:
    - Focus Child: {child_focus_name}
    - Activity: {child_activity}
    - Feeling: {child_feeling}

    Instructions:
    Use the teacher's notes and (optional) uploaded image to create:
    1. A joyful, simple description about {child_focus_name}'s moment.
    2. Write in a short, very fun, light-hearted, cheerful tone, like a preschool teacher talking excitedly to parents.
    Feel free to be playful and use cute or imaginative words, but keep it easy for parents to understand.
    3. Please do not mention the word "friend" and solely focus on {child_focus_name}
    4. Keep the quote UNDER 80 characters. Be creative and joyful!

    Ignore other children unless absolutely necessary.
    Keep everything friendly, warm, and appropriate for parent communication.
    """

    response = client.messages.create(
        model=model,
        max_tokens=150,
        temperature=temperature,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image # type: ignore
                        }
                    },
                    {
                        "type": "text",
                        "text": f"""
                        Here is a photo of {child_focus_name}.

                        Please describe the moment and generate a joyful quote based on the teacher's notes:
                        - Activity: {child_activity}
                        - Feeling: {child_feeling}

                        Focus only on {child_focus_name}. Ignore other children unless necessary.
                        """
                    }
                ]
            }
        ]
    )
    return response.content
