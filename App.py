import streamlit as st
import time
import os
import google.generativeai as genai
from dotenv import load_dotenv
import replicate

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Configure Gemini API with the loaded key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def replicate_copilot(code_snippet: str) -> str:
    model = "meta/codellama-70b-instruct:a279116fe47a0f65701a8817188601e2fe8f4b9e04a518789655ea7b995851bf"
    output = replicate.run(
        model,
        input={
            "prompt": f"Explain and improve this HTML/CSS/JS code, beginner‑friendly:\n{code_snippet}",
            "temperature": 0.7,
            "max_length": 512
        },
        token=os.getenv("REPLICATE_API_TOKEN")
    )
    return output[0] if isinstance(output, list) else output


def generate_content(prompt, temperature=0.7):
    start_time = time.time()
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt, generation_config={"temperature": temperature})
        end_time = time.time()
        return {
            'output': response.text,
            'generation_time': round(end_time - start_time, 2),
            'token_usage': {
                'prompt_tokens': "N/A",
                'completion_tokens': "N/A",
                'total_tokens': "N/A"
            }
        }
    except Exception as e:
        return {'error': str(e)}

# --- Prompt Templates ---
def get_prompt_template(template_type, topic, learner_level, context):
    if template_type == "Lesson Plan":
        return f"Create a comprehensive 1-hour lesson plan on '{topic}' for {learner_level} youth learning software development. Include learning objectives, materials needed, and step-by-step teaching activities. Context: {context}"
    elif template_type == "Study Guide":
        return f"Generate a study guide summarizing the key points of '{topic}' for {learner_level} students studying software development. Include bullet points and 5 quiz questions. Context: {context}"
    elif template_type == "Tutorials":
        return f"Design a group-based hands-on activity to teach the topic '{topic}' to {learner_level} learners. Ensure it's engaging and collaborative. Context: {context}"
    elif template_type == "Quiz Answer Sheet":
        return f"Provide an answer sheet for a 5-question quiz on the topic '{topic}' in software development. Context: {context}"
    elif template_type == "Topic Summary":
        return f"Summarize the topic '{topic}' in simple terms for {learner_level} students beginning their software development journey. Context: {context}"
    elif template_type == "Try it yourself":
        return f"Generate a hands-on practice exercise for learners on the topic '{topic}' in software development. The activity should include a description, starter code, and instructions to complete the task. Target Level: {learner_level}. Context: {context}"
    return ""

# --- Streamlit UI ---
st.set_page_config(page_title="Software Dev Content Generator", layout="centered")
st.title("💻 CODESNACK")

# Practice Arena toggle
show_practice_arena = st.sidebar.checkbox("🧪 Practice Arena")

# Sidebar Input
with st.sidebar:
    st.header("🔧 Start Learning")
    template_type = st.selectbox("Select Content Type:", ["Lesson Plan", "Try it yourself", "Tutorials", "Quiz Answer Sheet", "Topic Summary"])
    topic = st.text_input("Software Dev Topic:", "")
    learner_level = st.selectbox("Learning Level:", ["Beginner", "Intermediate", "Advanced"])
    context = st.text_area("Add Context (Optional):", "")
    generate_btn = st.button("🚀 Generate Content")

# Content Generation Section
if generate_btn:
    prompt = get_prompt_template(template_type, topic, learner_level, context)
    st.subheader("Prompt Sent to Gemini:")
    st.code(prompt, language='markdown')

    with st.spinner("Generating content..."):
        result = generate_content(prompt)

    if 'error' in result:
        st.error(f"❌ Error: {result['error']}")
    else:
        st.success("✅ Content generated successfully!")
        st.subheader("Output:")
        st.text_area("Generated Output:", result['output'], height=300)
        st.download_button("📥 Download Output", result['output'], file_name=f"{template_type}_{topic}.txt")

# --- Custom Prompt Feature ---
st.markdown("---")
st.header("✍️ Start Typing")

custom_prompt = st.text_area("Custom Prompt")

if st.button("✨ Start Generating"):
    if custom_prompt.strip() == "":
        st.warning("Please enter a valid prompt before generating.")
    else:
        with st.spinner("Generating custom response..."):
            custom_result = generate_content(custom_prompt)

        if 'error' in custom_result:
            st.error(f"❌ Error: {custom_result['error']}")
        else:
            st.success("✅ Custom content generated successfully!")
            st.text_area("Custom Output:", custom_result['output'], height=150)
            st.json({
                "Generation Time (s)": custom_result['generation_time'],
                "Prompt Tokens": custom_result['token_usage']['prompt_tokens'],
                "Completion Tokens": custom_result['token_usage']['completion_tokens'],
                "Total Tokens": custom_result['token_usage']['total_tokens']
            })
            st.download_button("📥 Download Custom Output", custom_result['output'], file_name="custom_prompt_output.txt")

# --- PRACTICE ARENA ---
if show_practice_arena:
    st.markdown("---")
    st.header("🧪 Practice Arena: HTML/CSS/JS Exercises")

    activity = st.selectbox("Choose an Activity:", [
        "Basic HTML Page",
        "CSS Styling Example",
        "Simple JS Alert",
        "Interactive Button"
    ])

    if activity == "Basic HTML Page":
        starter_code = """
<!DOCTYPE html>
<html>
  <body>
    <h1>Welcome!</h1>
    <p>This is a basic HTML page.</p>
  </body>
</html>
"""
    elif activity == "CSS Styling Example":
        starter_code = """
<!DOCTYPE html>
<html>
  <head>
    <style>
      p { color: blue; font-size: 20px; }
    </style>
  </head>
  <body>
    <p>This paragraph is styled with CSS!</p>
  </body>
</html>
"""
    elif activity == "Simple JS Alert":
        starter_code = """
<!DOCTYPE html>
<html>
  <body>
    <h2>Click the button for a message</h2>
    <button onclick="alert('Hello from JavaScript!')">Click Me</button>
  </body>
</html>
"""
    elif activity == "Interactive Button":
        starter_code = """
<!DOCTYPE html>
<html>
  <body>
    <button onclick="document.getElementById('demo').innerHTML='You clicked me!'">Click me</button>
    <p id="demo"></p>
  </body>
</html>
"""

    user_code = st.text_area("✍️ Edit Your Code Below", starter_code, height=300)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Run Code"):
            styled_html = f"""
            <div style="background-color:white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                {user_code}
            </div>
            """
            st.components.v1.html(styled_html, height=400, scrolling=True)

    with col2:
        if st.button("🤖 Get Help from Replicate Copilot"):
            with st.spinner("Sending code to Replicate model..."):
                try:
                    explanation = replicate_copilot(user_code)
                    st.success("✅ Copilot Response:")
                    st.text_area("🔍 Explanation & Suggestions", explanation, height=300)
                except Exception as e:
                    st.error(f"❌ Error from Replicate: {str(e)}")
