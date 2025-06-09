import streamlit as st
import openai
import time
import os

# Load OpenAI API key securely from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to call the OpenAI API
def generate_content(prompt, temperature=0.7, max_tokens=600):
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

# Prompt templates specifically for Software Development Education
def get_prompt_template(template_type, topic, learner_level, context):
    if template_type == "Lesson Plan":
        return f"Create a comprehensive 1-hour lesson plan on '{topic}' for {learner_level} youth learning software development. Include learning objectives, materials needed, and step-by-step teaching activities. Context: {context}"
    elif template_type == "Study Guide":
        return f"Generate a study guide summarizing the key points of '{topic}' for {learner_level} students studying software development. Include bullet points and 5 quiz questions. Context: {context}"
    elif template_type == "Group Activity":
        return f"Design a group-based hands-on activity to teach the topic '{topic}' to {learner_level} learners. Ensure it's engaging and collaborative. Context: {context}"
    elif template_type == "Quiz Answer Sheet":
        return f"Provide an answer sheet for a 5-question quiz on the topic '{topic}' in software development. Context: {context}"
    elif template_type == "Topic Summary":
        return f"Summarize the topic '{topic}' in simple terms for {learner_level} students beginning their software development journey. Context: {context}"
    return ""

# --- Streamlit UI ---
st.set_page_config(page_title="Software Dev Content Generator", layout="centered")
st.title("💻 Custom Content Generator for Youth in Software Development")

with st.sidebar:
    st.header("🔧 Customize Your Content")
    template_type = st.selectbox("Select Content Type:", ["Lesson Plan", "Study Guide", "Group Activity", "Quiz Answer Sheet", "Topic Summary"])
    topic = st.text_input("Software Dev Topic:", "Variables in Python")
    learner_level = st.selectbox("Learning Level:", ["Beginner", "Intermediate", "Advanced"])
    context = st.text_area("Add Context (Optional):", "Teach rural youth with no programming experience.")
    temperature = st.slider("Creativity (Temperature):", 0.0, 1.0, 0.7)
    generate_btn = st.button("🚀 Generate Content")

if generate_btn:
    prompt = get_prompt_template(template_type, topic, learner_level, context)
    st.subheader("📋 Prompt Preview")
    st.code(prompt, language='markdown')

    with st.spinner("Generating content..."):
        result = generate_content(prompt, temperature)

    if 'error' in result:
        st.error(f"❌ Error: {result['error']}")
    else:
        st.success("✅ Content generated successfully!")
        st.subheader("📄 Generated Output")
        st.text_area("Output:", result['output'], height=300)

        st.markdown("### 📊 Performance Metrics")
        st.json({
            "Generation Time (s)": result['generation_time'],
            "Prompt Tokens": result['token_usage']['prompt_tokens'],
            "Completion Tokens": result['token_usage']['completion_tokens'],
            "Total Tokens": result['token_usage']['total_tokens']
        })

        st.download_button("📥 Download Output", result['output'], file_name=f"{template_type}_{topic}.txt")

# --- Custom Prompt Feature ---
st.markdown("---")
st.header("✍️ Write Your Own Custom Prompt")

custom_prompt = st.text_area("Enter your own AI prompt below (e.g., 'Explain loops in Python for kids with no coding background'):")

if st.button("✨ Generate from Custom Prompt"):
    if custom_prompt.strip() == "":
        st.warning("Please enter a valid prompt before generating.")
    else:
        with st.spinner("Generating custom response..."):
            custom_result = generate_content(custom_prompt, temperature)

        if 'error' in custom_result:
            st.error(f"❌ Error: {custom_result['error']}")
        else:
            st.success("✅ Custom content generated successfully!")
            st.text_area("Custom Output:", custom_result['output'], height=300)
            st.json({
                "Generation Time (s)": custom_result['generation_time'],
                "Prompt Tokens": custom_result['token_usage']['prompt_tokens'],
                "Completion Tokens": custom_result['token_usage']['completion_tokens'],
                "Total Tokens": custom_result['token_usage']['total_tokens']
            })
            st.download_button("📥 Download Custom Output", custom_result['output'], file_name="custom_prompt_output.txt")
