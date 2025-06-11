import streamlit as st
from io import BytesIO
import time
import os
import re
import google.generativeai as genai
from dotenv import load_dotenv
import replicate

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

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
    
#Function | Remove the asterisk
def remove_all_asterisks(text):
    # Remove **double asterisks**
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)

    # Remove *single asterisks*
    text = re.sub(r'\*(.*?)\*', r'\1', text)

    return text

#Function | Convert to pdf
def text_to_pdf(text, filename):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Set initial position and font
    x, y = A4[0]/8, A4[1]-50
    font_name = "Helvetica"
    font_size = 12
    c.setFont(font_name, font_size)
    
    # Line height calculation
    line_height = font_size * 1.2  # Adjust multiplier as needed
    # Split the text into lines
    lines = text.splitlines()
    
    # Maximum characters per line (adjust as needed based on font and margins)
    max_chars_per_line = 90
    
    for line in lines:
        # If the line is too long, split it into multiple lines
        while len(line) > max_chars_per_line:
            # Find the last space within the limit
            split_index = line[:max_chars_per_line].rfind(' ')
            if split_index == -1:
                # If no space is found, force split at the limit
                split_index = max_chars_per_line
            
            part = line[:split_index]
            line = line[split_index+1:]  # +1 to remove the space
            
            # Check if we need a new page
            if y < 50:  # 50 is the bottom margin
                c.showPage()
                x, y = A4[0]/8, A4[1]-50
                c.setFont(font_name, font_size)
            
            c.drawString(x, y, part)
            y -= line_height
        
        # Writes the remaining part of the line
        # Check if we need a new page
        if y < 50:  # 50 is the bottom margin
            c.showPage()
            x, y = A4[0]/8, A4[1]-50
            c.setFont(font_name, font_size)
            
        c.drawString(x, y, line)
        y -= line_height
    c.save()
    buffer.seek(0)
    return buffer

# Prompt templates specifically for Software Development Education
def get_prompt_template(template_type, topic, learner_level, context):
    base_prompt = ""
    if template_type == "Lesson Plan":
        base_prompt = f"Create a comprehensive 1-hour lesson plan on '{topic}' for {learner_level} youth learning software development. Include learning objectives, materials needed, and step-by-step teaching activities. Context: {context}"
    elif template_type == "Study Guide":
        base_prompt = f"Generate a study guide summarizing the key points of '{topic}' for {learner_level} students studying software development. Include bullet points and 5 quiz questions. Context: {context}"
    elif template_type == "Tutorials":
        base_prompt =  f"Design a group-based hands-on activity to teach the topic '{topic}' to {learner_level} learners. Ensure it's engaging and collaborative. Context: {context}"
    elif template_type == "Quiz Answer Sheet":
        base_prompt = f"Provide an answer sheet for a 5-question quiz on the topic '{topic}' in software development. Context: {context}"
    elif template_type == "Topic Summary":
        base_prompt = f"Summarize the topic '{topic}' in simple terms for {learner_level} students beginning their software development journey. Context: {context}"
    elif template_type == "Try it yourself":
        base_prompt == f"Generate a hands-on practice exercise for learners on the topic '{topic}' in software development. The activity should include a description, starter code, and instructions to complete the task. Target Level: {learner_level}. Context: {context}"
           
    #instructions to add emojis that's relevant where needed
    base_prompt += "\n\nMake sure to add relevant emojis next to important points or headings instead of using bold formatting. If there are lists, use either unordered lists (bullets) or ordered lists (numbers) — do not use asterisks (*) for lists. Ensure the text is presented cleanly and neatly."
    return base_prompt

# --- Streamlit UI ---
st.set_page_config(page_title="CodeSnack", page_icon="favicon.ico", layout="centered")
st.image("codesnack.png")

# Global variable to store performance data
if 'performance_data' not in st.session_state:
    st.session_state.performance_data = {}
    
# Practice Arena toggle
show_practice_arena = st.sidebar.checkbox("🧪 Practice Arena")

# Sidebar Input
with st.sidebar:
    st.header("🧠 Start Learning")
    template_type = st.selectbox("Select Content Type:", ["Lesson Plan", "Try it yourself", "Tutorials", "Quiz Answer Sheet", "Topic Summary"])
    topic = st.text_input("Software Dev Topic:", "")
    learner_level = st.selectbox("Learning Level:", ["Beginner", "Intermediate", "Advanced"])
    context = st.text_area("Add Context (Optional):", "")
   
    generate_btn = st.button("🚀 Generate Content")
    evaluate_btn = st.button("📊 Evaluate Performance")

# Content Generation Section
if generate_btn:
    prompt = get_prompt_template(template_type, topic, learner_level, context)
    st.subheader("Prompt Sent to Gemini:")
    st.subheader("Request sent:")
    st.code(prompt, language='markdown')

    with st.spinner("Generating content..."):
        start_time = time.time()
        result = generate_content(prompt)
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)

        # Store performance
        st.session_state.performance_data = {
            "response_time": elapsed_time,
            "content_length": len(result['output']) if 'output' in result else 0
        }
    if 'error' in result:
        st.error(f"❌ Error: {result['error']}")
    else:
        st.success("✅ Content generated successfully!")
        st.subheader("Output:")
        
        #removing the asterisk from the result
        remove_asterisk_from_result = remove_all_asterisks(result['output'])
        st.text_area("Generated Output:", remove_asterisk_from_result, height=300)
        
        #replace asterisk with nothing
        remove_asterisk_from_result_file = remove_all_asterisks(result['output']) 
        
        # Convert text to PDF
        pdf_buffer = text_to_pdf(remove_asterisk_from_result_file, f"{template_type}_{topic}.pdf")  
         
        st.download_button("📥 Download Output", data=pdf_buffer, file_name=f"{template_type}_{topic}.pdf", mime="application/pdf")


# Evaluate Performance
if evaluate_btn:
    if st.session_state.performance_data:
        st.sidebar.markdown("### 📈 Performance Report")
        st.sidebar.write(f"🕒 Response Time: `{st.session_state.performance_data['response_time']}s`")
        st.sidebar.write(f"📝 Output Length: `{st.session_state.performance_data['content_length']} characters`")
    else:
        st.sidebar.warning("⚠️ No performance data yet. Generate content first.")

# --- Custom Prompt Feature ---
st.header("✍️ What would you like to ask?")
# Initialize session state for the custom prompt if it doesn't exist
if "custom_prompt" not in st.session_state:
    st.session_state.custom_prompt = ""

# Text input for the prompt
custom_prompt = st.text_area("", value=st.session_state.custom_prompt)
st.session_state.custom_prompt = custom_prompt  # Sync session state with user input
# New Prompt button clears everything

col1, spacer, col2 = st.columns([1, 0.96, 1])

with col2:
    if st.button("🔄 Clear"):
        st.session_state.custom_prompt = ""  # Clear the prompt
        st.rerun()
              # Rerun the app to clear outputs
# Start Generating button
with col1:
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
            
            #Remove the custome result asterisk
            remove_custom_result_asterisk = remove_all_asterisks(custom_result['output'])
            st.text_area("Custom Output:", custom_result['output'], height=300)
            st.json({
                "Generation Time (s)": custom_result['generation_time'],
                "Prompt Tokens": custom_result['token_usage']['prompt_tokens'],
                "Completion Tokens": custom_result['token_usage']['completion_tokens'],
                "Total Tokens": custom_result['token_usage']['total_tokens']
            })
            
            #replace asterisk with nothing
            remove_asterisk_from_file = remove_all_asterisks(custom_result['output'])
            
            # Convert text to PDF
            pdf_buffer_custom = text_to_pdf(remove_asterisk_from_file, "custom_prompt_output.pdf")
            
            st.download_button("📥 Download Custom Output", data=pdf_buffer_custom, file_name="custom_prompt_output.pdf", mime="application/pdf")


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
        if st.button("▶️ Run Code", key="run_code_button"):
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
