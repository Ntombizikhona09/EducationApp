import streamlit as st
import openai
import time
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Use environment variable for security

# Function to call the OpenAI API
def generate_content(prompt, temperature=0.7, max_tokens=500):
    start_time = time.time()
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        end_time = time.time()
        usage = response['usage']
        return {
            'output': response.choices[0].message['content'],
            'token_usage': usage,
            'generation_time': round(end_time - start_time, 2)
        }
    except Exception as e:
        return {'error': str(e)}

# Prompt templates
def get_prompt_template(template_type, topic, grade_level, subject):
    if template_type == "Lesson Plan":
        return f"Create a comprehensive 1-hour lesson plan on '{topic}' for {grade_level} students studying {subject}. Include objectives, materials, and step-by-step activities."
    elif template_type == "Study Guide":
        return f"Generate a study guide summarizing key concepts of '{topic}' for {grade_level} students in {subject}, including bullet points and sample quiz questions."
    elif template_type == "Activity Idea":
        return f"Provide a hands-on activity idea to teach the concept of '{topic}' to {grade_level} students learning {subject}."
    elif template_type == "Worksheet":
        return f"Create a student worksheet with answer key on '{topic}' for {grade_level} {subject} class. Include 5-10 questions."
    elif template_type == "Topic Summary":
        return f"Summarize the topic '{topic}' in simple terms for {grade_level} students studying {subject}."
    return ""

# Streamlit UI
st.title("🎓 Educational Content Generator")

with st.sidebar:
    st.header("Customize Content")
    template_type = st.selectbox("Select Content Type:", ["Lesson Plan", "Study Guide", "Activity Idea", "Worksheet", "Topic Summary"])
    topic = st.text_input("Topic:", "Photosynthesis")
    grade_level = st.selectbox("Grade Level:", ["Grade 4", "Grade 6", "Grade 8", "High School", "College"])
    subject = st.selectbox("Subject:", ["Biology", "History", "Math", "Literature", "Physics"])
    temperature = st.slider("Creativity (Temperature):", 0.0, 1.0, 0.7)
    generate_btn = st.button("Generate Content")

if generate_btn:
    prompt = get_prompt_template(template_type, topic, grade_level, subject)
    st.subheader("📋 Prompt Preview")
    st.code(prompt, language='markdown')

    with st.spinner("Generating content..."):
        result = generate_content(prompt, temperature)

    if 'error' in result:
        st.error(f"Error: {result['error']}")
    else:
        st.success("Content generated successfully!")
        st.markdown("---")
        st.subheader("📄 Generated Output")
        st.text_area("Output:", result['output'], height=300)

        st.markdown("---")
        st.subheader("📊 Performance Metrics")
        st.json({
            "Generation Time (s)": result['generation_time'],
            "Prompt Tokens": result['token_usage']['prompt_tokens'],
            "Completion Tokens": result['token_usage']['completion_tokens'],
            "Total Tokens": result['token_usage']['total_tokens']
        })

        st.download_button("Download Output", result['output'], file_name=f"{template_type}_{topic}.txt")
